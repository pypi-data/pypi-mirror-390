"""
Run cvlib from command line
"""

import sys
import cvlib

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = sys.argv[1]
        if task == "all":
            cvlib.show_all()
        else:
            try:
                task_num = int(task)
                if 1 <= task_num <= 9:
                    func = getattr(cvlib, f"show_task_{task_num}")
                    func()
                else:
                    print("Task number must be between 1 and 9")
            except ValueError:
                print("Usage: python -m cvlib [1-9|all]")
    else:
        print("CVLIB - Computer Vision Library")
        print("=" * 50)
        print("Usage: python -m cvlib [task_number]")
        print("\nExamples:")
        print("  python -m cvlib 1     # Show task 1 code")
        print("  python -m cvlib 5     # Show task 5 code")
        print("  python -m cvlib all   # Show all tasks")
        print("\nOr import in Python:")
        print("  import cvlib")
        print("  cvlib.show_task_1()")
        print("  cvlib.show_all()")
