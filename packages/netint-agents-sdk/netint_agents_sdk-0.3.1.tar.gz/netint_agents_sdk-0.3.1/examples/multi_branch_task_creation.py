"""
Multi-branch task creation example.

This example demonstrates how to create a task with multiple Git branches
using the create_with_instance convenience method.
"""

from netint_agents_sdk import NetIntClient, NetIntConfig


def main():
    # Create client
    config = NetIntConfig(
        base_url="http://10.0.10.125:8888",
        api_token="your_api_token_here",
        timeout=600,  # 10 minutes for instance creation
        debug=True
    )
    client = NetIntClient(config)

    try:
        print("=== Creating Task with Multiple Branches ===\n")

        # Create a task with multiple branches pre-fetched
        task = client.tasks.create_with_instance(
            title="Compare branch differences",
            prompt="Compare the differences between main, develop, and staging branches",
            environment_id=66,
            description="Multi-branch comparison task",
            ask_mode=False,
            additional_branches="develop,staging,hotfix/urgent"  # ← NEW PARAMETER!
        )

        print(f"✅ Task created with multiple branches!")
        print(f"   Task ID: {task.id}")
        print(f"   Title: {task.title}")
        print(f"   Instance URL: {task.instance_url}")
        print(f"\n   Available branches in instance:")
        print(f"   - main (primary branch)")
        print(f"   - develop")
        print(f"   - staging")
        print(f"   - hotfix/urgent")
        print(f"\n   All branches are ready to use immediately! 🎉")

        # Example: You can now work with any branch in the instance
        print("\n=== Example Commands You Can Run ===")
        print("# Switch to develop branch")
        print(f"git checkout develop")
        print("\n# Compare branches")
        print(f"git diff main..develop")
        print("\n# List all branches")
        print(f"git branch -a")

    finally:
        client.close()


def example_with_feature_branches():
    """Example: Working with feature branches"""
    config = NetIntConfig(
        base_url="http://10.0.10.125:8888",
        api_token="your_api_token_here",
        timeout=600,
        debug=True
    )
    client = NetIntClient(config)

    try:
        print("\n=== Feature Branch Development Example ===\n")

        # Create task for feature branch work
        task = client.tasks.create_with_instance(
            title="Review new authentication feature",
            prompt="Review and test the authentication changes in feature/new-auth branch",
            environment_id=66,
            description="Feature branch review and testing",
            ask_mode=False,
            additional_branches="feature/new-auth,develop"  # Feature + develop branches
        )

        print(f"✅ Feature branch task created!")
        print(f"   Instance has branches: main, feature/new-auth, develop")
        print(f"   Ready to review feature branch against develop and main")

    finally:
        client.close()


def example_release_testing():
    """Example: Release testing across multiple environments"""
    config = NetIntConfig(
        base_url="http://10.0.10.125:8888",
        api_token="your_api_token_here",
        timeout=600,
        debug=True
    )
    client = NetIntClient(config)

    try:
        print("\n=== Release Testing Example ===\n")

        # Create task for release testing
        task = client.tasks.create_with_instance(
            title="Test release candidate",
            prompt="Run tests against release/v2.0 and compare with production",
            environment_id=66,
            description="Release testing and validation",
            ask_mode=False,
            additional_branches="release/v2.0,production,staging"
        )

        print(f"✅ Release testing task created!")
        print(f"   Instance has branches:")
        print(f"   - main")
        print(f"   - release/v2.0 (candidate)")
        print(f"   - production (current)")
        print(f"   - staging (testing)")
        print(f"\n   Perfect for comprehensive release validation! 🚀")

    finally:
        client.close()


def example_backward_compatible():
    """Example: Single branch (backward compatible)"""
    config = NetIntConfig(
        base_url="http://10.0.10.125:8888",
        api_token="your_api_token_here",
        timeout=600,
        debug=True
    )
    client = NetIntClient(config)

    try:
        print("\n=== Single Branch (Backward Compatible) ===\n")

        # Create task without additional_branches (backward compatible)
        task = client.tasks.create_with_instance(
            title="Simple single-branch task",
            prompt="Work on main branch only",
            environment_id=66,
            description="Traditional single-branch workflow",
            ask_mode=False
            # No additional_branches parameter - works exactly as before
        )

        print(f"✅ Single-branch task created!")
        print(f"   Instance has only: main")
        print(f"   Backward compatible - no changes needed to existing code!")

    finally:
        client.close()


if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  Multi-Branch Task Creation Examples                     ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    # Run main example
    main()

    # Uncomment to run other examples:
    # example_with_feature_branches()
    # example_release_testing()
    # example_backward_compatible()

    print("\n✨ All examples completed!")
