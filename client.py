"""FIX GATEWAY"""
import sys
import argparse
import quickfix
from threading import Thread
import app

def main(config_file):
    """Main"""
    try:
        settings = quickfix.SessionSettings(config_file)
        application = app.Application()
        storefactory = quickfix.FileStoreFactory(settings)
        logfactory = quickfix.FileLogFactory(settings)
        initiator = quickfix.SocketInitiator(application, storefactory, settings, logfactory)

        initiator.start()
        application.run()
        initiator.stop()

    except (quickfix.ConfigError, quickfix.RuntimeError) as e:
        print(e)
        #initiator.stop()
        sys.exit()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='FIX Client')
    parser.add_argument('file_name', type=str, help='Name of configuration file')
    args = parser.parse_args()
    Thread(target=app.run_server).start()
    main(args.file_name)