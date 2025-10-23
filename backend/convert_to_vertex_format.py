"""
Convert ranking training data to Vertex AI format.

This script converts the structured JSONL format to Vertex AI's expected format:
- input_text: Combined prompt with all features
- output_text: The target relevance score
"""
import json
import sys
from pathlib import Path


def convert_to_vertex_format(
    input_file: str = "output/ranking_training_data.jsonl",
    output_file: str = "output/vertex_ready.jsonl"
):
    """
    Convert structured JSONL to Vertex AI format.
    
    Args:
        input_file: Path to original JSONL file
        output_file: Path to output Vertex-ready JSONL file
    """
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    # Ensure input file exists
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        print("   Run: python prepare_ranking_data.py")
        return False
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("  Converting to Vertex AI Format")
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
                
                # Check for required fields
                required_fields = ['query', 'category', 'title', 'rank', 
                                   'recency_score', 'user_engagement_score', 
                                   'relevance_score']
                
                missing_fields = [f for f in required_fields if f not in data]
                if missing_fields:
                    print(f"  Warning: Line {line_num} missing fields: {missing_fields}")
                    skipped_count += 1
                    continue
                
                # Create the input prompt
                prompt = (
                    f"query: {data['query']}\n"
                    f"category: {data['category']}\n"
                    f"title: {data['title']}\n"
                    f"rank: {data['rank']}\n"
                    f"recency_score: {data['recency_score']}\n"
                    f"user_engagement_score: {data['user_engagement_score']}\n\n"
                    f"Predict a relevance score between 0 and 1."
                )
                
                # Create the output (target score as string)
                response = str(data['relevance_score'])
                
                # Write in Vertex AI format
                vertex_doc = {
                    "input_text": prompt,
                    "output_text": response
                }
                
                json.dump(vertex_doc, outfile, ensure_ascii=False)
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
    print("Sample of converted format:")
    print("-" * 60)
    
    with open(output_path, "r", encoding="utf-8") as f:
        sample = json.loads(f.readline())
        print(f"\ninput_text:\n{sample['input_text']}")
        print(f"\noutput_text: {sample['output_text']}")
    
    print()
    print("-" * 60)
    print()
    print("✓ Ready to upload to Google Cloud Storage!")
    print("  Next steps:")
    print("  1. Upload to GCS: gsutil cp output/vertex_ready.jsonl gs://your-bucket/")
    print("  2. Go to Vertex AI Model Garden")
    print("  3. Select your model (Gemini/Text-Bison)")
    print("  4. Click 'Tune model' and point to your GCS file")
    print()
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert ranking data to Vertex AI format"
    )
    parser.add_argument(
        "--input",
        default="output/ranking_training_data.jsonl",
        help="Input JSONL file (default: output/ranking_training_data.jsonl)"
    )
    parser.add_argument(
        "--output",
        default="output/vertex_ready.jsonl",
        help="Output Vertex-ready JSONL file (default: output/vertex_ready.jsonl)"
    )
    
    args = parser.parse_args()
    
    success = convert_to_vertex_format(args.input, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

