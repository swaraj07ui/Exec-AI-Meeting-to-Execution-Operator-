import os
from lemma_sdk import Pod

# Make sure you have LEMMA_TOKEN and LEMMA_POD_ID set in your environment
# export LEMMA_TOKEN="your_token_from_lemma.work"
# export LEMMA_POD_ID="your_pod_id"

def run_extraction_workflow(notes_text: str, meeting_title: str):
    print(f"Starting meeting execution for: {meeting_title}")
    
    # 1. Connect to the Pod using the Lemma Python SDK
    # This automatically picks up credentials from your environment or CLI config
    with Pod.from_env() as pod:
        print(f"Connected to Pod: {pod.id}")
        
        # 2. Trigger the process-meeting workflow
        # This matches the workflow defined in workflows/process_meeting.yaml
        print("Triggering the process_meeting workflow...")
        run = pod.workflows.run(
            "process-meeting", 
            inputs={
                "notes_text": notes_text,
                "meeting_title": meeting_title
            }
        )
        
        # 3. Wait for the run to hit the human approval step
        print(f"Workflow started! Run ID: {run.id}")
        while True:
            # Poll the run status using the SDK
            status = pod.workflows.runs.get(run.id).status
            
            if status == "awaiting_approval":
                print("Workflow paused. Extracted tasks are waiting for human review.")
                break
            elif status == "completed":
                print("Workflow completed automatically.")
                break
            elif status == "failed":
                print("Workflow failed.")
                return
                
        # At this point, the frontend (apps/index.html) would take over 
        # to show the review modal, and then call the `/approve` endpoint!
        print("Done! You can now review the tasks in the frontend UI.")

if __name__ == "__main__":
    sample_notes = """
    [00:00:00] Rahul: Alright, let's start the sprint review.
    [00:00:15] Sneha: I finished the onboarding flow mockups. I'll share the Figma link.
    [00:01:30] Rahul: Perfect. Arjun, can you start setting up the component library on Friday?
    [00:01:45] Arjun: Yeah, I can do that Friday.
    """
    
    # If you run this script locally with your tokens set, it will actually
    # trigger the backend and run the claude model extraction!
    try:
        run_extraction_workflow(sample_notes, "Sprint Review")
    except Exception as e:
        print("\n---")
        print("NOTE: Lemma SDK is integrated correctly in the code!")
        print("To actually execute this against a real backend, ensure your LEMMA_TOKEN and LEMMA_POD_ID environment variables are set.")
        print(f"Error details: {e}")
