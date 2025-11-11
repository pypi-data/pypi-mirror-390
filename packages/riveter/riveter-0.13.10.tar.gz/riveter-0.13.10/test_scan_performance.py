#!/usr/bin/env python3
"""Test scan command performance with actual Terraform files."""

import os
import subprocess
import tempfile
import time


def create_test_terraform_file():
    """Create a simple test Terraform file."""
    tf_content = """
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"

  tags = {
    Name = "test-instance"
  }
}

resource "aws_s3_bucket" "example" {
  bucket = "my-test-bucket"
}
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
        f.write(tf_content)
        return f.name


def create_test_rules_file():
    """Create a simple test rules file."""
    rules_content = """
metadata:
  name: test-rules
  version: 1.0.0
  description: Test rules for performance testing
  author: Test

rules:
  - id: test-rule-1
    description: Test that instances have tags
    resource_type: aws_instance
    severity: warning
    assert:
      tags: exists
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(rules_content)
        return f.name


def main():
    """Test scan command performance."""
    print("🔍 Testing Scan Command Performance")
    print("=" * 50)

    # Create test files
    tf_file = create_test_terraform_file()
    rules_file = create_test_rules_file()

    try:
        print(f"📄 Created test Terraform file: {tf_file}")
        print(f"📋 Created test rules file: {rules_file}")

        # Test scan command
        command = [
            "python3",
            "-c",
            "from src.riveter.cli import main; main()",
            "scan",
            "--rules",
            rules_file,
            "--terraform",
            tf_file,
            "--output-format",
            "json",
        ]

        print("\n🚀 Running scan command...")
        print(f"Command: {' '.join(command)}")

        start_time = time.time()
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        end_time = time.time()

        duration = end_time - start_time

        print("\n📊 Results:")
        print(f"   Duration: {duration:.3f}s")
        print(f"   Exit code: {result.returncode}")
        print(f"   Stdout length: {len(result.stdout)} chars")
        print(f"   Stderr length: {len(result.stderr)} chars")

        if result.returncode == 0:
            print("   ✅ Scan completed successfully")
            if duration <= 5.0:
                print("   ✅ Performance target met (≤5s)")
            else:
                print("   ⚠️  Performance target missed (>5s)")
        else:
            print("   ❌ Scan failed")
            if result.stderr:
                print(f"   Error: {result.stderr}")

        # Show some output if available
        if result.stdout and len(result.stdout) < 1000:
            print("\n📄 Output preview:")
            print(result.stdout[:500])

    finally:
        # Clean up test files
        try:
            os.unlink(tf_file)
            os.unlink(rules_file)
            print("\n🧹 Cleaned up test files")
        except OSError:
            pass


if __name__ == "__main__":
    main()
