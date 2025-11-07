import argparse
import logging
import os

from prophecy_lineage_extractor.reader import get_reader, RestPipelineProcessor


def main():
    parser = argparse.ArgumentParser(description="Prophecy Lineage Extractor")
    parser.add_argument("--project-id", type=str, required=True, help="Prophecy Project ID")
    parser.add_argument("--pipeline-id", type=str, required=False, nargs='+', help="Prophecy Pipeline ID(s)")
    parser.add_argument("--model-id", type=str, required=False, nargs='+', help="Prophecy Model ID(s)")
    parser.add_argument("--send-email", action="store_true", help="Enable verbose output")
    parser.add_argument("--branch", type=str, default="default", help="Branch to run lineage extractor on")
    parser.add_argument("--reader", type=str, default="lineage", help="Read Via 'lineage' backend or 'knowledge-graph' backend to run lineage extractor on")
    # parser.add_argument("--non-recursive-extract", action="store_true", help="Whether to Recursively include Upstream Source Transformations")
    parser.add_argument("--run-for-all", action="store_true", help="Whether to Create Project Level Sheet")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory inside the project")
    parser.add_argument("--fmt", type=str, required=False, help="What format to write to")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level")

    args = parser.parse_args()

    # Configure logging with the specified log level
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.info(f"Logging level set to {args.log_level}")

    reader_str = args.reader
    pipeline_output_dir = os.path.join(args.output_dir)
    os.makedirs(pipeline_output_dir, exist_ok=True)
    reader_obj = get_reader(reader_str)
    run_for_all = args.run_for_all
    # Validation logic for pipeline_id requirement
    # If run_for_all provided and reader type is RestPipelineProcessor, then allow when pipeline_id not defined
    if reader_obj == RestPipelineProcessor and run_for_all:
        # pipeline_id is optional when using RestPipelineProcessor with run_for_all=True
        pipeline_id_str = args.pipeline_id[0] if args.pipeline_id else ""
        logging.info(f"Running for all pipelines in project using {reader_str} reader - pipeline-id and model-id are optional ")
        model_id_str = args.model_id[0] if args.model_id else ""
    else:
        # pipeline_id is required in all other cases
        if not args.pipeline_id and not args.model_id:
            raise Exception("pipeline-id or model-id is required when run_for_all=False or when not using RestPipelineProcessor")
        elif args.fmt == "openlineage" and not run_for_all:
            raise Exception("Openlineage is currently only supported in run_for_all set to True")
        if args.pipeline_id:
            pipeline_id_str = args.pipeline_id[0]
        else:
            pipeline_id_str = ""
        if args.model_id:
            model_id_str = args.model_id[0]
        else:
            model_id_str = ""
        logging.info(f"Running for specific pipeline: {pipeline_id_str} and model: {model_id_str} using {reader_str} reader")


    # Initialize reader with appropriate parameters
    reader = reader_obj(
        project_id=args.project_id,
        branch=args.branch,
        output_dir=pipeline_output_dir,
        send_email=args.send_email,
        non_recursive_extract= False, #args.non_recursive_extract,
        run_for_all=run_for_all,
        fmt=args.fmt if args.fmt else 'excel',
        pipeline_id_str=pipeline_id_str,
        model_id_str=model_id_str,
    )

    # Process the lineage extraction
    reader.process()
    # reader.writer.write()


if __name__ == "__main__":
    main()