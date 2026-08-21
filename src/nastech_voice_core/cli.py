"""Command-line interface for Nastech Voice Core TTS.

This module provides a command-line interface for easy text-to-speech
synthesis, batch processing, and model management.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from . import __version__
from .config import AVAILABLE_LANGUAGES, AVAILABLE_MODELS, DEFAULT_MODEL
from .pipeline import TTS

logger = logging.getLogger(__name__)


def cmd_say(args):
    """Generate speech and play it directly without saving a file."""
    # Setup logging based on verbose flag
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    # Check if sounddevice is installed
    try:
        import sounddevice as sd
    except ImportError:
        print("❌ Error: sounddevice is required for the 'say' command.")
        print("   Install it with: pip install supertonic[playback]")
        print("   Or: pip install sounddevice")
        sys.exit(1)

    if args.verbose:
        print(f"🎤 Generating speech: {args.text[:50]}...")

    try:
        # Initialize TTS
        print(f"Loading model ({args.model})...")
        load_start = time.time()
        tts = TTS(model=args.model)
        load_time = time.time() - load_start
        print(f"   -> Model loaded in {load_time:.2f}s")

        # Text processing
        if args.verbose:
            print("Processing text...")
            text_start = time.time()

            # Show text validation
            is_valid, unsupported = tts.model.text_processor.validate_text(args.text)
            # Show preprocessed text
            preprocessed = tts.model.text_processor._preprocess_text(args.text)

            text_time = time.time() - text_start
            print(f"   -> Text processed in {text_time:.3f}s")

            print(f"   Original: {args.text[:80]}{'...' if len(args.text) > 80 else ''}")
            if not is_valid:
                print(f"   ⚠️  Unsupported chars: {unsupported[:10]}")
            if preprocessed != args.text:
                print(
                    f"   Preprocessed: {preprocessed[:80]}{'...' if len(preprocessed) > 80 else ''}"
                )

        # Get voice style
        print(f"Loading voice style ({args.custom_style_path or args.voice})...")
        style_start = time.time()
        if args.custom_style_path:
            voice_style = tts.get_voice_style_from_path(args.custom_style_path)
        else:
            voice_style = tts.get_voice_style(args.voice)
        style_time = time.time() - style_start
        print(f"   -> Voice style loaded in {style_time:.3f}s")

        # Generate speech
        print(f"Generating speech (lang={args.lang or 'auto'})...")
        start_time = time.time()
        wav, duration = tts.synthesize(
            args.text,
            voice_style=voice_style,
            total_steps=args.steps,
            speed=args.speed,
            max_chunk_length=args.max_chunk_length,
            silence_duration=args.silence_duration,
            lang=args.lang,
            verbose=args.verbose,
        )
        elapsed_time = time.time() - start_time
        print(f"   -> Speech generated in {elapsed_time:.2f}s")

        # Play audio directly
        print(f"Playing {duration[0]:.2f}s audio...")
        sd.play(wav.squeeze(), tts.sample_rate)
        sd.wait()  # Wait until audio is finished playing
        print("   -> Audio played")

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            logger.exception("TTS playback failed with exception:")
        sys.exit(1)


def cmd_tts(args):
    """Generate speech from text using TTS."""
    # Setup logging based on verbose flag
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    if args.verbose:
        print(f"🎤 Generating speech: {args.text[:50]}...")

    try:
        # Initialize TTS
        print(f"Loading model ({args.model})...")
        load_start = time.time()
        tts = TTS(model=args.model)
        load_time = time.time() - load_start
        print(f"   -> Model loaded in {load_time:.2f}s")

        # Text processing
        if args.verbose:
            print("Processing text...")
            text_start = time.time()

            # Show text validation
            is_valid, unsupported = tts.model.text_processor.validate_text(args.text)
            # Show preprocessed text
            preprocessed = tts.model.text_processor._preprocess_text(args.text)

            text_time = time.time() - text_start
            print(f"   -> Text processed in {text_time:.3f}s")

            print(f"   Original: {args.text[:80]}{'...' if len(args.text) > 80 else ''}")
            if not is_valid:
                print(f"   ⚠️  Unsupported chars: {unsupported[:10]}")
            if preprocessed != args.text:
                print(
                    f"   Preprocessed: {preprocessed[:80]}{'...' if len(preprocessed) > 80 else ''}"
                )

        # Get voice style
        print(f"Loading voice style ({args.custom_style_path or args.voice})...")
        style_start = time.time()
        if args.custom_style_path:
            voice_style = tts.get_voice_style_from_path(args.custom_style_path)
        else:
            voice_style = tts.get_voice_style(args.voice)
        style_time = time.time() - style_start
        print(f"   -> Voice style loaded in {style_time:.3f}s")

        # Generate speech
        print(f"Generating speech (lang={args.lang or 'auto'})...")
        start_time = time.time()
        wav, duration = tts.synthesize(
            args.text,
            voice_style=voice_style,
            total_steps=args.steps,
            speed=args.speed,
            max_chunk_length=args.max_chunk_length,
            silence_duration=args.silence_duration,
            lang=args.lang,
            verbose=args.verbose,
        )
        elapsed_time = time.time() - start_time
        print(f"   -> Speech generated in {elapsed_time:.2f}s")

        # Save audio
        print(f"Saving {duration[0]:.2f}s audio to {args.output}...")
        tts.save_audio(wav, args.output)
        print(f"   -> Audio saved to {args.output}")

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            logger.exception("TTS generation failed with exception:")
        sys.exit(1)


def cmd_list_voices(args):
    """List available voice styles."""
    try:
        tts = TTS()
        styles = tts.voice_style_names

        print(f"📢 Available voice styles ({len(styles)}):\n")
        for style in styles:
            print(f"  • {style}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def cmd_info(args):
    """Show model information."""
    try:
        tts = TTS()

        print("ℹ️  Nastech Voice Core Model Information\n")
        print(f"Model directory: {tts.model_dir}")
        print(f"Sample rate: {tts.sample_rate} Hz")
        print(f"\nAvailable voice styles: {', '.join(tts.voice_style_names)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def cmd_download(args):
    """Download model from HuggingFace."""
    from .loader import download_model, get_cache_dir

    print("📥 Downloading Nastech Voice Core model...")

    try:
        cache_dir = get_cache_dir()
        download_model(cache_dir)
        print(f"✅ Model downloaded to: {cache_dir}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        sys.exit(1)


def cmd_version(args):
    """Show version information."""
    print(f"supertonic {__version__}")


def cmd_serve(args):
    """Run a local HTTP server exposing /v1/tts and friends."""
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    try:
        import uvicorn

        from .server import create_app
    except ImportError:
        print("❌ Error: fastapi and uvicorn are required for the 'serve' command.")
        print("   Install them with: pip install supertonic[serve]")
        sys.exit(1)

    if args.host not in ("127.0.0.1", "localhost", "::1"):
        # Bind to anything other than loopback is opt-in. Print a one-line
        # warning so an accidental ``--host 0.0.0.0`` is visible.
        print(
            f"⚠️  Warning: binding to {args.host} exposes the server beyond loopback. "
            "Add auth at a reverse proxy if this is intentional.",
            file=sys.stderr,
        )

    cors_origins = None
    if args.cors:
        cors_origins = [o.strip() for o in args.cors.split(",") if o.strip()]

    app = create_app(model=args.model, cors_origins=cors_origins)

    print(f"supertonic serve listening on http://{args.host}:{args.port}")
    print(f"  docs:  http://{args.host}:{args.port}/docs")
    print(f"  model: {args.model}")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        # uvicorn's reload mode requires an import string, not an app instance.
        # We don't support it here — power users can run uvicorn directly
        # against ``supertonic.server:create_app`` if they want reload.
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and return the CLI argument parser.

    This function is separated to allow documentation generation tools
    to extract CLI arguments automatically.

    Returns:
        ArgumentParser configured with all Nastech Voice Core CLI commands
    """
    parser = argparse.ArgumentParser(
        prog="supertonic",
        description="Nastech Voice Core - High-quality Text-to-Speech synthesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate and play speech directly (no file saved)
  supertonic say 'Hello, welcome to the world!'

  # Generate speech from text and save to file
  supertonic tts 'Hello, welcome to the world!' -o output.wav

  # Use different voice and quality
  supertonic say 'This is a female voice style.' --voice F1 --steps 10
  supertonic tts 'This is a female voice style.' -o hello.wav --voice F1 --steps 10

  # Multilingual support (supertonic-3 covers 31 languages — see --lang choices)
  supertonic say '안녕하세요! 반갑습니다.' --lang ko
  supertonic tts 'Bonjour le monde!' -o french.wav --lang fr
  supertonic tts 'Hola, bienvenido!' -o spanish.wav --lang es

  # Unknown / unsupported language fallback (supertonic-3)
  supertonic say 'Some uncommon text' --lang na

  # Use custom voice style from JSON file
  supertonic say 'This is a custom voice test.' --custom-style-path ./my_voice.json

  # Long text with custom chunking
  supertonic tts 'This is a very long text.' -o output.wav --max-chunk-length 200

  # List available voices
  supertonic list-voices
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Common arguments helper function
    def add_common_args(p):
        p.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose output with detailed logging",
        )

    # Say command (play audio directly without saving)
    parser_say = subparsers.add_parser(
        "say", help="Generate speech and play it directly without saving a file"
    )
    parser_say.add_argument("text", help="Text to synthesize and play")
    parser_say.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        choices=AVAILABLE_MODELS,
        help=(
            "Model to use: supertonic (English only), supertonic-2 (5 languages), "
            f"or supertonic-3 (31 languages + 'na' fallback). Default: {DEFAULT_MODEL}"
        ),
    )
    parser_say.add_argument("--voice", default="M1", help="Voice style (default: M1)")
    parser_say.add_argument(
        "--custom-style-path",
        type=str,
        default=None,
        help="Path to custom voice style JSON file (overrides --voice if provided)",
    )
    parser_say.add_argument(
        "--lang",
        type=str,
        default=None,
        choices=AVAILABLE_LANGUAGES,
        metavar="LANG",
        help=(
            "Language code (supertonic-3): "
            "en, ko, ja, ar, bg, cs, da, de, el, es, et, fi, fr, hi, hr, hu, "
            "id, it, lt, lv, nl, pl, pt, ro, ru, sk, sl, sv, tr, uk, vi, "
            "or 'na' for unknown / unsupported languages. "
            "Default: 'na' for multilingual models (supertonic-2/3), "
            "'en' for supertonic v1."
        ),
    )
    parser_say.add_argument(
        "--steps", type=int, default=8, help="Quality steps (default: 8, higher=better)"
    )
    parser_say.add_argument(
        "--speed",
        type=float,
        default=1.05,
        help="Speech speed (0.7-2.0, default: 1.05, 2.0=2x faster)",
    )
    parser_say.add_argument(
        "--max-chunk-length",
        type=int,
        default=None,
        help="Maximum characters per chunk (default: auto based on language)",
    )
    parser_say.add_argument(
        "--silence-duration",
        type=float,
        default=0.3,
        help="Silence between chunks in seconds (default: 0.3)",
    )
    add_common_args(parser_say)
    parser_say.set_defaults(func=cmd_say)

    # TTS command
    parser_tts = subparsers.add_parser("tts", aliases=["t"], help="Generate speech from text")
    parser_tts.add_argument("text", help="Text to synthesize")
    parser_tts.add_argument("-o", "--output", required=True, help="Output WAV file")
    parser_tts.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        choices=AVAILABLE_MODELS,
        help=(
            "Model to use: supertonic (English only), supertonic-2 (5 languages), "
            f"or supertonic-3 (31 languages + 'na' fallback). Default: {DEFAULT_MODEL}"
        ),
    )
    parser_tts.add_argument("--voice", default="M1", help="Voice style (default: M1)")
    parser_tts.add_argument(
        "--custom-style-path",
        type=str,
        default=None,
        help="Path to custom voice style JSON file (overrides --voice if provided)",
    )
    parser_tts.add_argument(
        "--lang",
        type=str,
        default=None,
        choices=AVAILABLE_LANGUAGES,
        metavar="LANG",
        help=(
            "Language code (supertonic-3): "
            "en, ko, ja, ar, bg, cs, da, de, el, es, et, fi, fr, hi, hr, hu, "
            "id, it, lt, lv, nl, pl, pt, ro, ru, sk, sl, sv, tr, uk, vi, "
            "or 'na' for unknown / unsupported languages. "
            "Default: 'na' for multilingual models (supertonic-2/3), "
            "'en' for supertonic v1."
        ),
    )
    parser_tts.add_argument(
        "--steps", type=int, default=8, help="Quality steps (default: 8, higher=better)"
    )
    parser_tts.add_argument(
        "--speed",
        type=float,
        default=1.05,
        help="Speech speed (0.7-2.0, default: 1.05, 2.0=2x faster)",
    )
    parser_tts.add_argument(
        "--max-chunk-length",
        type=int,
        default=None,
        help="Maximum characters per chunk (default: auto based on language)",
    )
    parser_tts.add_argument(
        "--silence-duration",
        type=float,
        default=0.3,
        help="Silence between chunks in seconds (default: 0.3)",
    )
    add_common_args(parser_tts)
    parser_tts.set_defaults(func=cmd_tts)

    # Backward compatibility: synthesize command (deprecated)
    parser_synth = subparsers.add_parser(
        "synthesize", aliases=["s"], help="(Deprecated: use tts) Generate speech from text"
    )
    parser_synth.add_argument("text", help="Text to synthesize")
    parser_synth.add_argument("-o", "--output", required=True, help="Output WAV file")
    parser_synth.add_argument("--voice", default="M1", help="Voice style (default: M1)")
    parser_synth.add_argument(
        "--steps", type=int, default=8, help="Quality steps (default: 8, higher=better)"
    )
    add_common_args(parser_synth)
    parser_synth.set_defaults(func=cmd_tts)

    # List voices command
    parser_voices = subparsers.add_parser(
        "list-voices", aliases=["lv"], help="List available voice styles"
    )
    parser_voices.set_defaults(func=cmd_list_voices)

    # Info command
    parser_info = subparsers.add_parser("info", aliases=["i"], help="Show model information")
    parser_info.set_defaults(func=cmd_info)

    # Download command
    parser_download = subparsers.add_parser(
        "download", aliases=["d"], help="Download model from HuggingFace"
    )
    parser_download.set_defaults(func=cmd_download)

    # Version command
    parser_version = subparsers.add_parser(
        "version", aliases=["v"], help="Show version information"
    )
    parser_version.set_defaults(func=cmd_version)

    # Serve command — local HTTP wrapper. Installed via ``pip install supertonic[serve]``.
    parser_serve = subparsers.add_parser(
        "serve",
        help="Run a local HTTP server exposing /v1/tts (and OpenAI-compatible /v1/audio/speech)",
    )
    parser_serve.add_argument(
        "--host",
        default="127.0.0.1",
        help="Interface to bind (default: 127.0.0.1; loopback only)",
    )
    parser_serve.add_argument(
        "--port", type=int, default=7788, help="Port to listen on (default: 7788)"
    )
    parser_serve.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        choices=AVAILABLE_MODELS,
        help=f"Model to load on startup (default: {DEFAULT_MODEL})",
    )
    parser_serve.add_argument(
        "--cors",
        type=str,
        default=None,
        help=(
            "Comma-separated CORS origins to allow (e.g. "
            "'http://localhost:*,chrome-extension://*'). "
            "Omit to disable CORS entirely."
        ),
    )
    parser_serve.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="uvicorn log level (default: info)",
    )
    add_common_args(parser_serve)
    parser_serve.set_defaults(func=cmd_serve)

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()

    # Parse args
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
