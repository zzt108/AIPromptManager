import logging
import seqlog
import os
import time

def test_seq():
    seq_url = os.getenv("SEQ_URL", "http://localhost:5341")
    print(f"Testing Seq connection to: {seq_url}")
    
    # Configure seqlog directly
    seqlog.log_to_seq(
        server_url=seq_url,
        level=logging.INFO,
        batch_size=1,  # Force flush immediately
        auto_flush_timeout=1,
        override_root_logger=True
    )
    
    logging.info("Test log from AIPromptManager debug script {test_run_id}", test_run_id=int(time.time()))
    print("Log sent. Waiting 2 seconds...")
    time.sleep(2)
    print("Done.")

if __name__ == "__main__":
    test_seq()
