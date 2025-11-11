import logging
import os

import asmu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_asetup() -> None:
    """PyTest for the ASetup.
    This tests the serialization and deserialization of Interface properties to and from an ASetup.
    This test uses the `TestInterface` class, because the GitLab pipeline has no audio devices."""
    # create setup
    asetup = asmu.ASetup("./test_asetup_1.asmu")
    # create interface with all defaults,
    interface1 = asmu.Interface()

    # create iinputs and ioutputs and add parameters
    for ch in range(5):
        interface1.iinput(ch=ch, name=f"in{ch}")
        interface1.ioutput(ch=ch+1, name=f"in{ch+1}")
    interface1.iinput().reference = True
    interface1.ioutput(ch=3).reference = True

    # register asetup and save
    interface1.asetup = asetup
    asetup.save()

    # create other interface without paramters,
    # load setiings from asetup (of other interface),
    # and save as different filename
    asmu.Interface(asetup=asetup)
    asetup.save(path="./test_asetup_2.asmu")

    # create another interface with different parameters,
    interface3 = asmu.Interface(samplerate=96000,
                                blocksize=256)

    # create iinputs and ioutputs
    for ch in range(3):
        interface1.iinput(ch=ch+1)
        interface1.ioutput(ch=ch)

    # register asetup and save
    asetup.interface = interface3
    asetup.save(path="./test_asetup_3.asmu")

    # compare the files
    with open("./test_asetup_1.asmu", "r", encoding="utf-8") as f1, \
            open("./test_asetup_2.asmu", "r", encoding="utf-8") as f2, \
            open("./test_asetup_3.asmu", "r", encoding="utf-8") as f3:
        content_1 = f1.read()
        content_2 = f2.read()
        content_3 = f3.read()
        assert content_1 == content_2, "Files content do not match!"
        assert content_1 != content_3, "Files content match, allthough they shouldn't!"

    # remove files
    os.remove("./test_asetup_1.asmu")
    os.remove("./test_asetup_2.asmu")
    os.remove("./test_asetup_3.asmu")


if __name__ == "__main__":
    test_asetup()
