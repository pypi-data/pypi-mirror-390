#!/usr/bin/env python3
"""
Command-line interface for DeepSeek R1 Local
"""
import argparse
import sys
import os
from pathlib import Path
import subprocess

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="DeepSeek R1 Local - Offline AI Web UI with Council Deliberation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start the server
  deepseek-r1-local start
  
  # Download the TinyLlama model
  deepseek-r1-local download-model
  
  # Run with custom port
  deepseek-r1-local start --port 8080
  
  # Run with custom host
  deepseek-r1-local start --host 0.0.0.0
  
  # Show version
  deepseek-r1-local version
        """
    )
    
    parser.add_argument(
        "command",
        choices=["start", "download-model", "version", "info"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run the server on (default: 5000)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode"
    )
    
    parser.add_argument(
        "--model-dir",
        type=str,
        help="Custom model directory path"
    )
    
    args = parser.parse_args()
    
    if args.command == "version":
        from . import __version__
        print(f"DeepSeek R1 Local version {__version__}")
        return 0
    
    elif args.command == "info":
        print("=" * 60)
        print("DeepSeek R1 Local - Offline AI Web UI")
        print("=" * 60)
        print("\nFeatures:")
        print("  ✓ Offline AI Chat with TinyLlama model")
        print("  ✓ Web Search Integration (DuckDuckGo)")
        print("  ✓ Council Deliberation System (5 personas)")
        print("  ✓ Response Caching for Performance")
        print("  ✓ CPU-Optimized Inference")
        print("\nCouncil Members:")
        print("  - Dr. Logic (Analytical Rationalist)")
        print("  - Professor Sage (Historical Scholar)")
        print("  - Innovator Nova (Creative Visionary)")
        print("  - Advocate Heart (Empathetic Humanist)")
        print("  - Pragmatist Ray (Practical Realist)")
        print("\nCommands:")
        print("  start          - Start the web server")
        print("  download-model - Download TinyLlama model")
        print("  version        - Show version")
        print("  info           - Show this information")
        print("=" * 60)
        return 0
    
    elif args.command == "download-model":
        print("Downloading TinyLlama model...")
        print("This will download ~2.2GB of data")
        print()
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            model_dir = args.model_dir or "models/tinyllama"
            
            print(f"Downloading to: {model_dir}")
            print()
            
            print("Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            tokenizer.save_pretrained(model_dir)
            
            print("Downloading model...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                low_cpu_mem_usage=True
            )
            model.save_pretrained(model_dir)
            
            print()
            print("✓ Model downloaded successfully!")
            print(f"✓ Saved to: {model_dir}")
            
        except Exception as e:
            print(f"✗ Error downloading model: {e}")
            return 1
        
        return 0
    
    elif args.command == "start":
        print("=" * 60)
        print("Starting DeepSeek R1 Local Web UI")
        print("=" * 60)
        print()
        print(f"Host: {args.host}")
        print(f"Port: {args.port}")
        print(f"Debug: {args.debug}")
        print()
        print("Loading model... (this may take 1-2 minutes)")
        print()
        
        # Set environment variables
        if args.model_dir:
            os.environ["MODEL_DIR"] = args.model_dir
        
        # Import and run the app
        try:
            from .app import app, model_manager
            
            # Initialize model
            print("Initializing AI model...")
            model_manager.load_model()
            
            print()
            print("=" * 60)
            print(f"✓ Server ready at http://{args.host}:{args.port}")
            print("=" * 60)
            print()
            print("Features available:")
            print("  • AI Chat (toggle off Council mode)")
            print("  • Web Search (toggle on Search mode)")
            print("  • Council Deliberation (toggle on Council mode)")
            print()
            print("Press Ctrl+C to stop the server")
            print()
            
            # Run the Flask app
            app.run(
                host=args.host,
                port=args.port,
                debug=args.debug
            )
            
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            return 0
        except Exception as e:
            print(f"\n✗ Error starting server: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
