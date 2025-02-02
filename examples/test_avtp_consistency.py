import subprocess
import hashlib
import time
import os
import signal

def test_avtp_loopback():
    # Generate test data: 5 seconds of 1000Hz sine wave (16-bit, 2 channels) saved as test0.raw
    subprocess.run("sox -n -r 48000 -c 2 -b 16 test0.raw synth 5 sine 1000", shell=True, check=True)

    # Calculate MD5 checksum of test0.raw
    with open("test0.raw", "rb") as f:
        md5_orig = hashlib.md5(f.read()).hexdigest()
    print("Original data MD5 =", md5_orig)

    # Start listener
    listener = subprocess.Popen(
        "sudo ./aaf-listener -i lo -d 00:00:00:00:00:00",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for listener to start
    time.sleep(1)

    # Start talker
    subprocess.run(
        "cat test0.raw | sudo ./aaf-talker -i lo -d 00:00:00:00:00:00 -m 1000",
        shell=True,
        check=True
    )

    # Wait for listener to receive data
    time.sleep(3)

    # Terminate listener's process group
    os.killpg(os.getpgid(listener.pid), signal.SIGTERM)
    try:
        received_data, _ = listener.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        listener.kill()
        received_data, _ = listener.communicate()

    # Save listener output to received0.raw
    with open("received0.raw", "wb") as f:
        f.write(received_data)

    # Calculate MD5 checksum of received data
    md5_recv = hashlib.md5(received_data).hexdigest()
    print("Received data MD5 =", md5_recv)

    # Compare checksums to verify data consistency
    assert md5_orig == md5_recv, "Data mismatch!"
    print("Consistency test passed! MD5 =", md5_orig)

if __name__ == "__main__":
    test_avtp_loopback()
