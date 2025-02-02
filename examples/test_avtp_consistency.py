import subprocess
import hashlib
import time
import os
import signal

def test_avtp_loopback():
    # Generate test data: 5 seconds of 1000Hz sine wave (16-bit, 2 channels) in test0.raw
    subprocess.run("sox -n -r 48000 -c 2 -b 16 test0.raw synth 5 sine 1000", shell=True, check=True)

    # Compute MD5 checksum of the test data
    with open("test0.raw", "rb") as f:
        md5_orig = hashlib.md5(f.read()).hexdigest()
    print("Original data MD5 =", md5_orig)

    # Get sudo password from environment variable
    sudo_pass = os.environ.get("SUDO_PASS")
    if not sudo_pass:
        print("Please set the SUDO_PASS environment variable.")
        return

    # Start the listener first using -S to supply the password
    listener_cmd = f'echo "{sudo_pass}" | sudo -S ./aaf-listener -i lo -d 00:00:00:00:00:00'
    listener = subprocess.Popen(
        listener_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Allow time for the listener to initialize
    time.sleep(1)

    # Start the talker: send the test data using -S to supply the password
    talker_cmd = f'cat test0.raw | echo "{sudo_pass}" | sudo -S ./aaf-talker -i lo -d 00:00:00:00:00:00 -m 1000'
    subprocess.run(talker_cmd, shell=True, check=True)

    # Allow some time for the listener to receive the transmitted data
    time.sleep(3)

    # Force-terminate the listener by killing its process group
    os.killpg(os.getpgid(listener.pid), signal.SIGTERM)
    received_data, _ = listener.communicate(timeout=5)

    # Save the received data to received0.raw
    with open("received0.raw", "wb") as f:
        f.write(received_data)

    # Compute MD5 checksum of the received data
    md5_recv = hashlib.md5(received_data).hexdigest()
    print("Received data MD5 =", md5_recv)

    # Check for consistency
    assert md5_orig == md5_recv, "Data mismatch!"
    print("Consistency test passed! MD5 =", md5_orig)

if __name__ == "__main__":
    test_avtp_loopback()
