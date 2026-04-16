from invoke_example import main as run_invoke_example
from invoke_stream_example import main as run_invoke_stream_example
from model_list_example import main as run_model_list_example


def main() -> None:
    print("=== MODEL LIST EXAMPLE ===")
    run_model_list_example()
    print()

    print("=== INVOKE EXAMPLE ===")
    run_invoke_example()
    print()

    print("=== INVOKE STREAM EXAMPLE ===")
    run_invoke_stream_example()


if __name__ == "__main__":
    main()
