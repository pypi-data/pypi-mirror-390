"""Example: User onboarding workflow with email, payment, and signals."""

from worldflow import workflow, step, sleep, signal, parallel, RetryPolicy


@step(retries=RetryPolicy(max_attempts=3))
async def send_email(user_id: str, template: str) -> None:
    """Send an email to a user."""
    print(f"📧 Sending {template} email to user {user_id}")
    # Simulate email sending
    import asyncio
    await asyncio.sleep(0.1)
    print(f"✅ Email sent: {template}")


@step(retries=RetryPolicy(max_attempts=5, backoff="exponential"))
async def charge_card(user_id: str, amount_cents: int) -> str:
    """Charge a user's credit card."""
    print(f"💳 Charging user {user_id}: ${amount_cents/100:.2f}")
    # Simulate payment processing
    import asyncio
    await asyncio.sleep(0.2)
    payment_id = f"pay_{user_id}_{amount_cents}"
    print(f"✅ Payment successful: {payment_id}")
    return payment_id


@workflow
async def onboarding(user_id: str):
    """
    User onboarding workflow.
    
    1. Send welcome email
    2. Wait 3 days (durable sleep)
    3. Charge initial payment
    4. Send receipt and survey in parallel
    5. Wait for user's upgrade choice
    6. If upgrade chosen, charge upgrade fee
    """
    print(f"🚀 Starting onboarding for user {user_id}")
    
    # Step 1: Welcome email
    await send_email(user_id, "welcome")
    
    # Step 2: Wait 3 days (in production; for demo we'll use seconds)
    print("⏰ Sleeping for 3 seconds (represents 3 days)...")
    await sleep("3s")
    print("⏰ Sleep completed!")
    
    # Step 3: Charge card
    payment_id = await charge_card(user_id, 999)
    
    # Step 4: Send emails in parallel
    print("📬 Sending parallel emails...")
    await parallel([
        lambda: send_email(user_id, "receipt"),
        lambda: send_email(user_id, "survey"),
    ])
    
    # Step 5: Wait for user choice (webhook/signal)
    print("🔔 Waiting for user choice signal...")
    print(f"   Send signal with: worldflow signal <run_id> user_choice '\"upgrade\"'")
    choice = await signal("user_choice", timeout="7d")
    print(f"✅ Received choice: {choice}")
    
    # Step 6: Handle upgrade
    if choice == "upgrade":
        print("⬆️  User chose upgrade!")
        await charge_card(user_id, 4999)
        await send_email(user_id, "upgrade_confirmation")
    else:
        print("➡️  User chose standard plan")
    
    print(f"🎉 Onboarding complete for user {user_id}!")
    return {"user_id": user_id, "choice": choice, "payment_id": payment_id}


if __name__ == "__main__":
    # Run locally for testing
    import asyncio
    from uuid import uuid4
    from worldflow.worlds import LocalWorld
    from worldflow.runtime import Orchestrator
    
    async def main():
        world = LocalWorld()
        orchestrator = Orchestrator(world)
        
        run_id = f"run_{uuid4().hex[:12]}"
        print(f"Starting workflow with run_id: {run_id}")
        
        await orchestrator.start_workflow(
            run_id,
            onboarding,
            {"user_id": "user_123"},
            "onboarding"
        )
        
        # Wait a bit for async execution
        await asyncio.sleep(5)
        
        # Check status
        status = await world.get_run_status(run_id)
        print(f"\nWorkflow status: {status['status']}")
        
        if status['status'] == 'running':
            print(f"\nWorkflow is waiting for signal. Send it with:")
            print(f'  worldflow signal {run_id} user_choice \'"upgrade"\'')
    
    asyncio.run(main())

