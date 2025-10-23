"""
Convert ranking training data to Gemini conversational format.

This script converts JSONL to Gemini's required format:
- contents: array of user/model messages
- role: "user" or "model"
- parts: array containing text
"""
import json
import sys
from pathlib import Path


def convert_to_gemini_format(
    input_file: str = "output/vertex_ready.jsonl",
    output_file: str = "output/gemini_ready.jsonl"
):
    """
    Convert to Gemini conversational format.
    
    Args:
        input_file: Path to vertex_ready.jsonl or structured JSONL
        output_file: Path to output Gemini-ready JSONL file
    """
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    # Check which format the input file is in
    if not input_path.exists():
        # Try the structured format
        input_file = "output/ranking_training_data.jsonl"
        input_path = Path(input_file)
        
        if not input_path.exists():
            print(f"❌ Error: No input file found")
            print("   Expected: output/vertex_ready.jsonl or output/ranking_training_data.jsonl")
            print("   Run: python prepare_ranking_data.py")
            return False
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("  Converting to Gemini Conversational Format")
    print("=" * 60)
    print()
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()
    
    converted_count = 0
    skipped_count = 0
    
    with open(input_path, "r", encoding="utf-8") as infile, \
         open(output_path, "w", encoding="utf-8") as outfile:
        
        for line_num, line in enumerate(infile, 1):
            try:
                data = json.loads(line)
                
                # Check if it's already in vertex format (input_text/output_text)
                if "input_text" in data and "output_text" in data:
                    input_text = data["input_text"]
                    output_text = data["output_text"]
                else:
                    # Convert from structured format
                    required_fields = ['query', 'category', 'title', 'rank', 
                                       'recency_score', 'user_engagement_score', 
                                       'relevance_score']
                    
                    missing_fields = [f for f in required_fields if f not in data]
                    if missing_fields:
                        print(f"  Warning: Line {line_num} missing fields: {missing_fields}")
                        skipped_count += 1
                        continue
                    
                    # Create the input prompt
                    input_text = (
                        f"query: {data['query']}\n"
                        f"category: {data['category']}\n"
                        f"title: {data['title']}\n"
                        f"rank: {data['rank']}\n"
                        f"recency_score: {data['recency_score']}\n"
                        f"user_engagement_score: {data['user_engagement_score']}\n\n"
                        f"Predict a relevance score between 0 and 1."
                    )
                    output_text = str(data['relevance_score'])
                
                # Create Gemini conversational format
                gemini_doc = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": input_text
                                }
                            ]
                        },
                        {
                            "role": "model",
                            "parts": [
                                {
                                    "text": output_text
                                }
                            ]
                        }
                    ]
                }
                
                json.dump(gemini_doc, outfile, ensure_ascii=False)
                outfile.write("\n")
                
                converted_count += 1
                
                if converted_count % 100 == 0:
                    print(f"  Converted {converted_count} documents...")
                
            except json.JSONDecodeError as e:
                print(f"  Warning: Line {line_num} is not valid JSON: {e}")
                skipped_count += 1
            except Exception as e:
                print(f"  Warning: Line {line_num} failed: {e}")
                skipped_count += 1
    
    print()
    print("=" * 60)
    print("  Conversion Complete!")
    print("=" * 60)
    print()
    print(f"✓ Converted: {converted_count} documents")
    
    if skipped_count > 0:
        print(f"⚠ Skipped: {skipped_count} documents (errors or missing fields)")
    
    print()
    print(f"Output file: {output_file}")
    
    # Show file size
    file_size = output_path.stat().st_size
    print(f"File size: {file_size / 1024:.2f} KB")
    
    # Show sample
    print()
    print("-" * 60)
    print("Sample of Gemini format:")
    print("-" * 60)
    
    with open(output_path, "r", encoding="utf-8") as f:
        sample = json.loads(f.readline())
        print(json.dumps(sample, indent=2))
    
    print()
    print("-" * 60)
    print()
    print("✓ Ready to upload to Google Cloud Storage!")
    print()
    print("Next steps:")
    print("  1. Upload to GCS:")
    print(f"     gsutil cp {output_file} gs://your-bucket/gemini_ready.jsonl")
    print()
    print("  2. Fine-tune Gemini:")
    print("     ```python")
    print("     import vertexai")
    print("     from vertexai.tuning import sft")
    print()
    print("     vertexai.init(")
    print('         project="your-project-id",')
    print('         location="us-central1"')
    print("     )")
    print()
    print("     sft_tuning_job = sft.train(")
    print('         source_model="gemini-2.0-flash-001",')
    print(f'         train_dataset="gs://your-bucket/gemini_ready.jsonl",')
    print('         tuned_model_display_name="ranking-tuned-model"')
    print("     )")
    print("     ```")
    print()
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert ranking data to Gemini conversational format"
    )
    parser.add_argument(
        "--input",
        default="output/vertex_ready.jsonl",
        help="Input JSONL file (default: output/vertex_ready.jsonl)"
    )
    parser.add_argument(
        "--output",
        default="output/gemini_ready.jsonl",
        help="Output Gemini-ready JSONL file (default: output/gemini_ready.jsonl)"
    )
    
    args = parser.parse_args()
    
    success = convert_to_gemini_format(args.input, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

