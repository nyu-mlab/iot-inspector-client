"""
Main entry point for Inspector.

"""
import api_server


def main():
    api_server.start_local_api_server()


if __name__ == '__main__':
    main()
