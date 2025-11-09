from omnicart_pipeline.pipeline import OMNICartETL


def main():
    pipeline = OMNICartETL()
    pipeline.run()
    
if __name__ == "__main__":
    main()
    