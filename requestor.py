import argparse
import PatchArray
import Plotting
from PatchArray import GenerateElementArray, FieldSumPatchElement
import numpy as np
import asyncio
from yapapi import Executor, Task, WorkContext
from yapapi.log import enable_default_logger, log_summary, log_event_repr
from yapapi.package import vm
from datetime import timedelta

async def main(noPatches: int):
    print("MAIN" + str(noPatches))
    package = await vm.repo(
        image_hash="7c78a5c3da0f3ea1c03c8a87c4a1055c7d8035f2c108c4d9db443f56",
        min_mem_gib=0.5,
        min_storage_gib=2.0,
    )

    async def worker(ctx: WorkContext, tasks):
        print("WORKER")
        async for task in tasks:
            print("TASK: " + str(task.data))
            ctx.send_file('element' + str(task.data) + '.csv', "/golem/work/element.csv")
            ctx.send_file('physics.csv', "/golem/work/physics.csv")
            ctx.send_file('runPatch.py', "/golem/work/runPatch.py")
            ctx.send_file('RectPatch.py', "/golem/work/RectPatch.py")
            ctx.send_file('PatchArray.py', "/golem/work/PatchArray.py")
            ctx.send_file('ArrayFactor.py', "/golem/work/ArrayFactor.py")
            ctx.run("/bin/sh", "-c", f"python3 /golem/work/runPatch.py >> /golem/work/output.txt")
            ctx.download_file("/golem/work/output.txt", "output" + str(task.data) + ".txt")
            ctx.download_file("/golem/work/patchresult.csv", "patchresult" + str(task.data) + ".csv")
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
        print('Executor')
        async for task in executor.submit(worker, [Task(data=patchNo) for patchNo in range(noPatches)]):
            print('EXECUTOR DONE')
            # TODO - Pass freq
            # Plotting.generatePlots(noPatches, 14e9)
        print("HOW NOW?")
        Plotting.generatePlots(noPatches, 14e9)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Design Your Own Antenna Array - Powered By Golem')
    parser.add_argument('--freq', type=float, help='Frequency of operation', default=14e9)
    parser.add_argument('--width', type=float, help='Width Of Patch', default=10.7e-3)
    parser.add_argument('--length', type=float, help='Length Of Patch', default=10.7e-3)
    parser.add_argument('--h', type=float, help='Height of Patch', default=3e-3)
    parser.add_argument('--Er', type=float, help='Permittivity', default=2.5)
    parser.add_argument('--xpatches', type=int, help='Number of X Patches', default=2)
    parser.add_argument('--ypatches', type=int, help='Number of Y Patches', default=1)
    parser.add_argument('--patchSpace', type=float, help='Space Between Patches', default=0.06)

    args = parser.parse_args()
    freq = args.freq
    W = args.width
    L = args.length
    h = args.h
    Er = args.Er
    X_Patches = args.xpatches
    Y_Patches = args.ypatches
    patchSpace = args.patchSpace

    ElementArray = GenerateElementArray(X_Patches, Y_Patches, patchSpace)
    noPatches = len(ElementArray)

    for patchNo in range(noPatches):
        np.savetxt('element' + str(patchNo) + '.csv', ElementArray[patchNo], delimiter=',')
        np.savetxt('physics.csv', [freq, W, L, h, Er], delimiter=',')

    enable_default_logger()
    loop = asyncio.get_event_loop()
    task = loop.create_task(main(noPatches=noPatches))
    try:
        asyncio.get_event_loop().run_until_complete(task)
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        task.cancel()
        asyncio.get_event_loop().run_until_complete(task)
        print("DONE?")
        Plotting.generatePlots(noPatches, 14e9)

    """
    elementField = np.empty((noPatches, 360, 90))

    for patchNo in range(noPatches):
        element = np.genfromtxt('element' + str(patchNo) + '.csv', delimiter=',')
        physics = np.genfromtxt('physics.csv', delimiter=',')
        elementField[patchNo] = FieldSumPatchElement(element, physics[0], physics[1], physics[2], physics[3], physics[4])
        # elementField[patchNo] = FieldSumPatchElement(ElementArray[patchNo], freq, W, L, h, Er)
        # TODO - This will be saved from worker
        np.savetxt('./antenna/plotFiles/patch' + str(patchNo) + '.csv', elementField[patchNo], delimiter=',')

    Plotting.generatePlots(noPatches, freq)
    """
