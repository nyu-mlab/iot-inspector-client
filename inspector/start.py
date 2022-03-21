"""
Main entry point for Inspector.

"""
import apiserver


def main():
    apiserver.start_local_api_server()


if __name__ == '__main__':
    main()
