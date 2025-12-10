"""
Monthly investment letter generation workflow
Replicates the workflow defined in enter_challenge.rivet-project using OpenAI SDK
"""

from config import (
    PORTFOLIO_FILE,
    RISK_PROFILE_FILE,
    MACRO_ANALYSIS_FILE,
    OUTPUT_FILE,
    OUTPUT_DOCX_FILE,
    LOGO_FILE,
    DEFAULT_CITY,
    DEFAULT_SUBJECT,
    DEFAULT_CLOSING_LINE,
    DEFAULT_ADVISOR_TITLE,
    DEFAULT_GREETING_PREFIX,
    FINAL_PARAGRAPH_TEXT,
    PREVIEW_LENGTH,
)
from src import (
    read_file,
    write_file,
    summarize_portfolio,
    format_portfolio_summary,
    summarize_portfolio_results,
    summarize_risk_profile,
    summarize_macroeconomic_outlook,
    generate_investment_letter,
    create_letter,
    plot_portfolio_donut_with_inner_ring,
)


def main():
    """Main function that executes the complete workflow."""
    print("Starting investment letter generation workflow...")
    print("-" * 60)

    # Step 1: Read input files
    print("\n[1/5] Reading input files...")
    try:
        print(f"  ✓ Portfolio: {PORTFOLIO_FILE.name}")
        risk_profile_data = read_file(RISK_PROFILE_FILE)
        print(f"  ✓ Risk profile: {RISK_PROFILE_FILE.name}")
        macro_data = read_file(MACRO_ANALYSIS_FILE)
        print(f"  ✓ Macro analysis: {MACRO_ANALYSIS_FILE.name}")
    except Exception as e:
        print(f"  ✗ Error reading files: {str(e)}")
        return

    # Step 2: Process portfolio and calculate returns
    print("\n[2/5] Processing portfolio and calculating returns...")
    try:
        print("  → Parsing portfolio data...")
        portfolio_summary = summarize_portfolio(PORTFOLIO_FILE)
        print("  ✓ Portfolio parsed")
        
        print("  → Formatting portfolio summary...")
        portfolio_formatted = format_portfolio_summary(portfolio_summary)
        print("  ✓ Portfolio summary formatted")
    except Exception as e:
        print(f"  ✗ Error processing portfolio: {str(e)}")
        return

    # Step 3: Generate AI summaries
    print("\n[3/5] Generating summaries with AI...")
    try:
        print("  → Generating risk profile summary...")
        risk_profile_summary = summarize_risk_profile(risk_profile_data)
        print("  ✓ Risk profile summary generated")
        
        print("  → Generating macroeconomic summary...")
        macro_outlook_summary = summarize_macroeconomic_outlook(macro_data)
        print("  ✓ Macroeconomic summary generated")
    except Exception as e:
        print(f"  ✗ Error generating summaries: {str(e)}")
        return

    # Step 4: Generate investment letter text
    print("\n[4/5] Generating investment letter...")
    try:
        investment_letter = generate_investment_letter(
            risk_profile_summary,
            macro_outlook_summary,
            portfolio_formatted
        )
        print("  ✓ Investment letter generated")
    except Exception as e:
        print(f"  ✗ Error generating letter: {str(e)}")
        return

    # Step 5: Create Word document with chart
    print("\n[5/5] Creating Word document...")
    try:
        # Use advisor information from portfolio, if available
        if portfolio_summary.advisor:
            sender_name = portfolio_summary.advisor.name
            sender_title = portfolio_summary.advisor.position
        else:
            sender_name = DEFAULT_ADVISOR_TITLE
            sender_title = DEFAULT_ADVISOR_TITLE
        
        # Use client name from portfolio
        recipient_name = f"{DEFAULT_GREETING_PREFIX} {portfolio_summary.client_name}"
        
        # Split investment letter into paragraphs
        body_paragraphs = investment_letter.split("\n\n")
        # Filter empty paragraphs and remove sign-off if present
        body_paragraphs = [
            p.strip() 
            for p in body_paragraphs 
            if p.strip() and not p.strip().startswith(DEFAULT_CLOSING_LINE.split(",")[0])
        ]
        
        # Generate portfolio chart
        print("  → Generating portfolio chart...")
        chart_figure = plot_portfolio_donut_with_inner_ring(
            portfolio_summary, 
            title=f"Distribuição do Portfólio - {portfolio_summary.client_name}"
        )
        print("  ✓ Portfolio chart generated")
        
        # Create Word document
        print("  → Creating Word document...")
        create_letter(
            output_file=OUTPUT_DOCX_FILE,
            image_path=str(LOGO_FILE),
            sender_name=sender_name,
            sender_title=sender_title,
            city=DEFAULT_CITY,
            recipient_name=recipient_name,
            subject_text=DEFAULT_SUBJECT,
            body_paragraphs=body_paragraphs,
            closing_line=DEFAULT_CLOSING_LINE,
            signature_name=sender_name,
            signature_title=sender_title,
            chart_figure=chart_figure
        )
        print(f"  ✓ Word document saved to: {OUTPUT_DOCX_FILE}")
        
        # Also save text version
        write_file(OUTPUT_FILE, investment_letter)
        print(f"  ✓ Text version saved to: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"  ✗ Error creating document: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("Workflow completed successfully!")
    print("=" * 60)
    
    # Display a preview of the letter
    print("\nPreview of generated letter:")
    print("-" * 60)
    if len(investment_letter) > PREVIEW_LENGTH:
        print(investment_letter[:PREVIEW_LENGTH] + "...")
    else:
        print(investment_letter)
    print("-" * 60)


if __name__ == "__main__":
    main()
