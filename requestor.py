import argparse
import Plotting
import os
import numpy as np
import asyncio
from yapapi import Executor, Task, WorkContext
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from yapapi.package import vm
from datetime import timedelta

def GenerateElementArray(X_Elements, Y_Elements, ElementSpacing):
    """
    Returns an empty numpy multidimensional array matching Element configuration.
    """
    noPatches = X_Elements * Y_Elements
    ElementArray = np.empty((noPatches, 5))
    if(Y_Elements == 1):
        # TO DO X = 1
        min = -1.0 * ((X_Elements/2 - 1) + 0.5) * ElementSpacing
        for xNo in range(X_Elements):
            ElementArray[xNo] = [min, 0, 0, 1, 0]
            min += ElementSpacing
    else:
        patchCount = 0
        minY = -1.0 * ((Y_Elements/2 - 1) + 0.5) * ElementSpacing
        for y in range(Y_Elements):
            minX = -1.0 * ((X_Elements/2 - 1) + 0.5) * ElementSpacing
            for x in range(X_Elements):
                ElementArray[patchCount] = [minX, minY, 0, 1, 0]
                minX += ElementSpacing
                patchCount += 1
            minY += ElementSpacing

    return ElementArray

async def main(args):
    print("Analysing " + str(args['noElements']) + " elements...")

    package = await vm.repo(
        image_hash="7c78a5c3da0f3ea1c03c8a87c4a1055c7d8035f2c108c4d9db443f56",
        min_mem_gib=0.5,
        min_storage_gib=2.0,
    )

    async def worker(ctx: WorkContext, tasks):
        print("WORKER")
        async for task in tasks:
            print("Worker for element no: " + str(task.data))
            # Sends current element info
            ctx.send_file('./elements/element' + str(task.data) + '.csv', "/golem/work/element.csv")
            # Sends physics file which contains freq, etc
            ctx.send_file('./elements/physics.csv', "/golem/work/physics.csv")
            # Send each file in element type folder. Must have an runAnalysis.py file. Allows for many different Element types to be analysed!
            for file in args['files']:
                print(f"Sending file: ./{type}/{file}")
                ctx.send_file(f'./{type}/{file}', f"/golem/work/{file}")

            print("Files sent, running analysis...")
            # Process for element
            ctx.run("/bin/sh", "-c", f"python3 /golem/work/runAnalysis.py >> /golem/work/output.txt")
            print("Downloading outputs...")
            # Can use to check processing ran ok
            ctx.download_file("/golem/work/output.txt", "./results/output" + str(task.data) + ".txt")
            # Actual result for element
            ctx.download_file("/golem/work/elementresult.csv", "./results/elementresult" + str(task.data) + ".csv")
            yield ctx.commit()
            task.accept_result()

    async with Executor(
        package=package,
        max_workers=3,
        budget=10.0,
        timeout=timedelta(minutes=10),
        subnet_tag="community.3",
        event_consumer=log_summary(),
    ) as executor:
        async for task in executor.submit(worker, [Task(data=elementNo) for elementNo in range(args['noElements'])]):
            print(f"Worker Done: {task}")


        print("Golem Jobs Complete. Processing results...")
        Plotting.generatePlots(args['noElements'], args['freq'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Design Your Own Antenna Array - Powered By Golem')
    parser.add_argument('--type', type=str, help='Element type', default="Patch")
    parser.add_argument('--freq', type=float, help='Frequency of operation', default=14e9)
    parser.add_argument('--width', type=float, help='Width Of Patch', default=10.7e-3)
    parser.add_argument('--length', type=float, help='Length Of Patch', default=10.7e-3)
    parser.add_argument('--h', type=float, help='Height of Patch', default=3e-3)
    parser.add_argument('--Er', type=float, help='Permittivity', default=2.5)
    parser.add_argument('--xelements', type=int, help='Number of X Elements', default=2)
    parser.add_argument('--yelements', type=int, help='Number of Y Elements', default=1)
    parser.add_argument('--spacing', type=float, help='Space Between Elements', default=0.06)
    # These are the variables a user can alter to design their array
    args = parser.parse_args()
    type = args.type
    freq = args.freq
    W = args.width
    L = args.length
    h = args.h
    Er = args.Er
    X_Elements = args.xelements
    Y_Elements = args.yelements
    spacing = args.spacing

    # Generate multidimensional array matching Element configuration
    ElementArray = GenerateElementArray(X_Elements, Y_Elements, spacing)
    noElements = len(ElementArray)

    # Save physics info (freq, etc) in file to pass to Golem workers
    np.savetxt('./elements/physics.csv', [freq, W, L, h, Er], delimiter=',')

    # Save each Element config in separate file to pass to Golem workers
    for elementNo in range(noElements):
        np.savetxt('./elements/element' + str(elementNo) + '.csv', ElementArray[elementNo], delimiter=',')

    """
    An element 'type' must have a matching folder in root dir.
    This folder should include all required scripts for analysing that specific element type along with a runAnalysis.py script.
    The runAnalysis.py is a common script that will be run by each worker. The script should run the analysis for that specific element
    (using files from element folder) and save the result in an elementresult.csv.
    This setup allows makes this solver easily extensible to analyse many different element types without the user requiring knowledge of the Golem system.
    """
    print(f"Analysing element type: {type}")
    directories = os.listdir(f"./{type}")
    if "runAnalysis.py" not in directories:
        print("Antenna Scripts Must Include A runAnalysis.py")
        sys.exit()

    golemArgs = { 'noElements': noElements, 'type': type, 'files': directories, 'freq': freq }

    enable_default_logger()
    loop = asyncio.get_event_loop()
    task = loop.create_task(main(args=golemArgs))
    try:
        asyncio.get_event_loop().run_until_complete(task)
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        task.cancel()
        asyncio.get_event_loop().run_until_complete(task)
