"""
Monthly investment letter generation workflow
Replicates the workflow defined in enter_challenge.rivet-project using OpenAI SDK
"""

from config import (
    PORTFOLIO_FILE,
    RISK_PROFILE_FILE,
    MACRO_ANALYSIS_FILE,
    OUTPUT_FILE,
)
from src import (
    read_file,
    write_file,
    summarize_portfolio_results,
    summarize_risk_profile,
    summarize_macroeconomic_outlook,
    generate_investment_letter,
)


def main():
    """Main function that executes the complete workflow."""
    print("Starting investment letter generation workflow...")
    print("-" * 60)

    # Step 1: Read input files
    print("\n[1/4] Reading input files...")
    try:
        portfolio_data = read_file(PORTFOLIO_FILE)
        print(f"  ✓ Portfolio read: {PORTFOLIO_FILE.name}")
        
        risk_profile_data = read_file(RISK_PROFILE_FILE)
        print(f"  ✓ Risk profile read: {RISK_PROFILE_FILE.name}")
        
        macro_data = read_file(MACRO_ANALYSIS_FILE)
        print(f"  ✓ Macro analysis read: {MACRO_ANALYSIS_FILE.name}")
    except Exception as e:
        print(f"  ✗ Error reading files: {str(e)}")
        return

    # Step 2: Generate summaries
    print("\n[2/4] Generating summaries with AI...")
    try:
        print("  → Generating portfolio summary...")
        portfolio_summary = summarize_portfolio_results(portfolio_data)
        print("  ✓ Portfolio summary generated")
        
        print("  → Generating risk profile summary...")
        risk_profile_summary = summarize_risk_profile(risk_profile_data)
        print("  ✓ Risk profile summary generated")
        
        print("  → Generating macroeconomic summary...")
        macro_outlook_summary = summarize_macroeconomic_outlook(macro_data)
        print("  ✓ Macroeconomic summary generated")
    except Exception as e:
        print(f"  ✗ Error generating summaries: {str(e)}")
        return

    # Step 3: Generate investment letter
    print("\n[3/4] Generating investment letter...")
    try:
        investment_letter = generate_investment_letter(
            risk_profile_summary,
            macro_outlook_summary,
            portfolio_summary
        )
        print("  ✓ Investment letter generated")
    except Exception as e:
        print(f"  ✗ Error generating letter: {str(e)}")
        return

    # Step 4: Save result
    print("\n[4/4] Saving result...")
    try:
        write_file(OUTPUT_FILE, investment_letter)
        print(f"  ✓ Letter saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"  ✗ Error saving file: {str(e)}")
        return

    print("\n" + "=" * 60)
    print("Workflow completed successfully!")
    print("=" * 60)
    
    # Display a preview of the letter
    print("\nPreview of generated letter:")
    print("-" * 60)
    preview_length = 500
    if len(investment_letter) > preview_length:
        print(investment_letter[:preview_length] + "...")
    else:
        print(investment_letter)
    print("-" * 60)


if __name__ == "__main__":
    main()
