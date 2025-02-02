import pyshark

def analyze_avtp_pcap(pcap_file, expected_payload):
    """
    Analyze AVTP packets in a pcap file and verify key fields.
    
    Parameters:
        pcap_file (str): The pcap file containing AVTP packets
        expected_payload (str): The expected payload value for comparison
    """
    cap = pyshark.FileCapture(
        pcap_file,
        display_filter='eth.type==0x22f0')
    
    prev_seq = None  # check sequence number continuity
    
    for pkt in cap:
        try:
            if hasattr(pkt, 'avtp_aaf'):
                avtp_layer = pkt.avtp_aaf
            
                # 1. sequence number check
                seq = int(avtp_layer.sequence_number)
                if prev_seq is not None:
                    expected_seq = (prev_seq + 1) % 256
                    if seq != expected_seq:
                        print(f"Sequence number discontinuity! Expected: {expected_seq}, Got: {seq}")
                prev_seq = seq
                
                # 2. timestamp check
                ts = int(avtp_layer.timestamp)
                
                # 3. payload check
                payload = avtp_layer.payload
                
                print(f"Seq: {seq}, Timestamp: {ts}")
                if payload != expected_payload:
                    print(f"Payload mismatch! Expected: {expected_payload}, Got: {payload}")
                else:
                    print(f"Payload match! Expected: {expected_payload}, Got: {payload}")
                    
        except AttributeError as e:
            print(f"Packet missing expected AVTP fields: {e}")
            
    cap.close()

if __name__ == "__main__":
    expected_payload = "your_expected_payload"  # replace with actual expected payload value
    analyze_avtp_pcap('avtp.pcap', expected_payload)
