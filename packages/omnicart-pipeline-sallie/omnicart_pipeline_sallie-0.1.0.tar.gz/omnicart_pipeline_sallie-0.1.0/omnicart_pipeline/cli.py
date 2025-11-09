#from pipeline.config import ConfigManager
from .pipeline import Pipeline

def main():
    pipeline = Pipeline()
    pipeline.run()

if __name__ == "__main__":
    main()