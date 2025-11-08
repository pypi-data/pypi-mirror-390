# KayGraph Batch Processing

**Difficulty**: ⭐⭐ (Intermediate)  
**Time**: ~15 minutes  
**Prerequisites**: [kaygraph-hello-world](../kaygraph-hello-world/), [kaygraph-workflow](../kaygraph-workflow/)

Basic batch processing example that translates a README file into multiple languages sequentially using KayGraph's BatchNode.

## What it does

This example demonstrates:
- **BatchNode Usage**: Process a list of items through the same logic
- **Sequential Processing**: Each translation happens one after another
- **Automatic Retry**: Built-in retry mechanism for failed items
- **Result Aggregation**: Collect and summarize all batch results

## Features

- Translates content into 10 different languages
- Saves each translation to a separate file
- Creates a summary with statistics
- Shows processing time for performance comparison

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the example
python main.py
```

### Code Example

```python
from kaygraph import BatchNode, Graph

class TranslationBatchNode(BatchNode):
    def prep(self, shared):
        # Return iterable of items to process
        languages = ["Spanish", "French", "German"]
        content = shared["content"]
        return [(content, lang) for lang in languages]
    
    def exec(self, item):
        # Process each item individually
        content, language = item
        return {"language": language, "translation": f"[{language}] {content}"}
    
    def post(self, shared, prep_res, exec_res):
        # Aggregate all results
        shared["translations"] = exec_res
        print(f"Translated into {len(exec_res)} languages!")
```

## Output

The example creates:
- `translations/` directory with translated files
- `translations/README_<language>.md` for each language
- `translations/translation_summary.json` with statistics

## Architecture

```
TranslationBatchNode
    ├── prep() → Create list of (content, language) tuples
    ├── exec() → Translate each item individually
    └── post() → Save translations and create summary
```

## Batch Processing Concepts

1. **Preparation Phase**: Create an iterable of items to process
2. **Execution Phase**: Process each item independently
3. **Post-processing Phase**: Aggregate results and perform cleanup

## Example Output

```
🌐 KayGraph Batch Translation Example
==================================================
Translating README into 10 languages...
This demonstrates sequential batch processing.

[INFO] Prepared 10 translation tasks
[INFO] Translating to Spanish...
[INFO] Saved Spanish translation to translations/readme_spanish.md
[INFO] Translating to French...
[INFO] Saved French translation to translations/readme_french.md
...

✅ Translation Summary:
  - Languages: Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese, Russian, Arabic
  - Total translations: 10
  - Output directory: translations/

⏱️  Processing time: 5.23 seconds
📊 Average time per translation: 0.52 seconds

💡 Note: For faster processing, see kaygraph-parallel-batch example!
```

## Performance

Sequential batch processing is simple but can be slow for I/O-bound tasks like API calls. For better performance with concurrent processing, see the `kaygraph-parallel-batch` example.

## Use Cases

- File format conversions
- Data transformations
- API batch operations
- Report generation
- Multi-language content generation

## 🧪 Experimentation

Try these modifications:
1. **Add error handling**: Make some translations fail randomly and handle errors
2. **Add progress tracking**: Show a progress bar during processing
3. **Change batch size**: Process in chunks instead of all at once

## 📚 Related Workbooks

- **[kaygraph-parallel-batch](../kaygraph-parallel-batch/)** - Speed up with concurrent processing
- **[kaygraph-nested-batch](../kaygraph-nested-batch/)** - Handle hierarchical batch operations
- **[kaygraph-batch-flow](../kaygraph-batch-flow/)** - Multiple batch nodes in sequence

## 🎓 Next Steps

After mastering sequential batch processing:
1. Learn parallel processing with `kaygraph-parallel-batch`
2. Explore error handling patterns in `kaygraph-fault-tolerant-workflow`
3. Build your own batch processing pipeline