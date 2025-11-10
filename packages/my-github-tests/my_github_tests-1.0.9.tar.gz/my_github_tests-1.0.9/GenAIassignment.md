# Take-home Interview Assignment
## Portfolio Performance Narrative Analysis

**Position:** Senior Quantitative Analyst / Portfolio Technology  
**Interviewer:** Portfolio Management Team  
**Date:** October 25, 2025  
**Time Allocation:** 4-6 hours

---

## Objective

Develop a Python-based system that analyzes portfolio position data and generates concise, factual narratives explaining what key themes and market events drove portfolio performance. This assignment evaluates your ability to combine quantitative analysis with real-world market context to produce executive-ready portfolio commentary.

**This assignment tests core job requirements:**
- **RAG System Implementation**: Design retrieval-augmented generation pipelines using LLMs with Python APIs (OpenAI, Anthropic, etc)
- **Financial Domain Expertise**: Multi-asset portfolio analysis and market context integration
- **Production-Ready Development**: Scalable code with robust source validation, attribution systems, and institutional-quality output

**Key Focus:** Create a narrative (maximum 10 sentences) that a portfolio manager could confidently present to clients or senior management, supported by both quantitative analysis and relevant market context.

---

## Background

In real-world portfolio management, stakeholders need clear explanations of performance that go beyond numbers. Your task is to build a system that:

1. **Analyzes** portfolio position data to identify key performance drivers
2. **Searches** for relevant market news and events during the reporting period
3. **Generates** professional narratives combining quantitative impact with qualitative context
4. **Validates** outputs for accuracy and business relevance

This mirrors production portfolio reporting where managers must quickly understand and communicate performance themes with supporting market context.

**Critical Requirement: Implement RAG (Retrieval-Augmented Generation) Methodology**

You must implement a RAG-based approach. This means:

- **Retrieval Phase**: Systematically retrieve and validate market context from external sources
- **Augmented Generation**: Ground all narrative generation in retrieved factual data
- **Source Attribution**: Cite all claims with specific sources and dates
- **Fact Verification**: Never speculate beyond retrieved information
- **Hallucination Prevention**: Ensure all generated content is supported by quantitative data or retrieved market context

The RAG methodology should minimize AI hallucinations by grounding every claim in either:
1. **Portfolio data** (quantitative metrics, returns, contributions)
2. **Retrieved market context** (news articles, corporate announcements, economic data)
3. **Validated external sources** (financial databases, regulatory filings)

---

## Data Provided

**File:** `PortfolioPositions.xlsx` (Sheet1)

**Data Structure:**
- **Security Information:** Ticker/CUSIP, issuer/company name, sector classification
- **Asset Types:** Equities (stocks), Fixed Income (government and corporate bonds), and Commodity
- **Pricing Data:** Start price (Price0), end price (Price1), calculated returns
- **Position Data:** Share/par quantities at period start and end
- **Valuation:** Current position values in USD
- **Period:** September 30, 2025 → October 24, 2025

**Portfolio Holdings Data:**

| name | crncy | security_des | ult_parent_ticker_exchange | asset_class | gics_sector_name | Price0 | Price1 | Return | Position0 | Position1 | ExchangeRateUSD0 | ExchangeRateUSD1 | CurrentValueUSD |
|------|-------|--------------|----------------------------|-------------|------------------|--------|--------|--------|-----------|-----------|------------------|------------------|----------------|
| CAT US Equity | USD | CATERPILLAR INC | CAT US | Equities | Industrials | 475.783 | 522.730 | 9.87% | 780 | 780 | 1.00 | 1.00 | 407,729.4 |
| IBM US Equity | USD | INTL BUSINESS MACHINES CORP | IBM US | Equities | Information Technology | 282.160 | 307.460 | 8.97% | 650 | 650 | 1.00 | 1.00 | 199,849 |
| HD US Equity | USD | HOME DEPOT INC | HD US | Equities | Consumer Discretionary | 405.190 | 386.680 | -4.57% | 720 | 720 | 1.00 | 1.00 | 278,409.6 |
| JPM US Equity | USD | JPMORGAN CHASE & CO | JPM US | Equities | Financials | 313.904 | 300.440 | -4.29% | 290 | 290 | 1.00 | 1.00 | 87,127.6 |
| NESN SW Equity | CHF | NESTLE SA-REG | NESN SW | Equities | Consumer Staples | 73.070 | 80.110 | 9.63% | 930 | 930 | 1.22 | 1.26 | 93,872.898 |
| AZN LN Equity | GBp | ASTRAZENECA PLC | AZN LN | Equities | Health Care | 11.182 | 12.532 | 12.07% | 860 | 860 | 1.30 | 1.35 | 14,549.652 |
| OR FP Equity | EUR | L'OREAL | OR FP | Equities | Consumer Staples | 368.500 | 374.700 | 1.68% | 800 | 800 | 1.18 | 1.15 | 344,724 |
| SPY US Equity | USD | SPDR S&P 500 ETF TRUST | STT US | Equities | Equity ETF | 666.180 | 677.250 | 1.66% | 450 | 450 | 1.00 | 1.00 | 304,762.5 |
| TLT US Equity | USD | ISHARES 20+ YEAR TREASURY BD | BLK US | Equities | Bond ETF | 89.059 | 91.470 | 2.71% | 5000 | 5000 | 1.00 | 1.00 | 457,350 |
| USO US Equity | USD | UNITED STATES OIL FUND LP | MGLD US | Commodity | Oil ETF | 73.750 | 73.180 | -0.77% | 820 | 820 | 1.00 | 1.00 | 60,007.6 |
| GLD US Equity | USD | SPDR GOLD SHARES | STT US | Commodity | Gold ETF | 355.470 | 377.520 | 6.20% | 600 | 600 | 1.00 | 1.00 | 226,512 |
| 91282CMM Govt | USD | US TREASURY N/B | 3352Z US | Government Bonds | Treasury Bond | 103.922 | 105.078 | 1.11% | 850 | 850 | 1.00 | 1.00 | 89,316.406 |
| BA 5.805 05/01/50 Corp | USD | BOEING CO | BA US | Corporate Bonds | IG Bond | 99.762 | 101.812 | 2.05% | 900 | 900 | 1.00 | 1.00 | 91,630.8 |
| BAC 5.015 07/22/33 Corp | USD | BANK OF AMERICA CORP | BAC US | Corporate Bonds | IG Bond | 102.271 | 103.106 | 0.82% | 690 | 690 | 1.00 | 1.00 | 71,143.14 |

---

## Core Requirements

### 1. Quantitative Analysis Engine

**Portfolio Metrics:**
- Calculate total portfolio return and contribution analysis across asset classes
- Identify top 3 positive and negative contributors by absolute impact (stocks and bonds)
- Separate equity vs. fixed income vs. commodity performance attribution
- Rank performance drivers by materiality across asset types

### 2. Market Context Integration (RAG Implementation)

**Retrieval Component:**
- **For Equities:** Search for news/events for top performing individual stocks during the period
- **For Bonds:** Search for issuer-level news and credit events affecting bond performance
- Focus on material corporate actions, earnings, acquisitions, regulatory changes, credit events
- Extract key facts that explain price movements for both asset classes
- Validate information sources and dates

**Augmented Generation Requirements:**
- All narrative claims must be grounded in either portfolio data or retrieved sources
- Implement source attribution for every factual statement
- Never generate speculative explanations not supported by retrieved context
- Implement confidence scoring for retrieved context quality

**Suggested Search Strategy:**
```python
def search_market_context(security_type: str, identifier: str, period: str) -> Dict:
    """
    Search for relevant market events during reporting period.
    Use available LLM APIs (OpenAI, Anthropic, local models) to generate 
    optimized search queries and analyze retrieved content.
    
    For equities: identifier = name or ticker (e.g., "CAT" or "CATERPILLAR INC")
    For bonds: identifier = issuer (e.g., "Bank of America", "US Treasury")
    
    Returns: {
        'primary_driver': str,
        'event_date': str, 
        'price_reaction': str,
        'context_summary': str,
        'source_url': str,   # Citation source
        'confidence_score': float,  # 0.0-1.0 reliability rating
        'retrieval_timestamp': str
    }
    """
```

### 3. Narrative Generation

**Recommended Structure Requirements:**
1. **Opening:** Overall portfolio performance with period specification and asset class breakdown
2. **Asset Class Theme:** Leading asset class (equity vs. fixed income) with quantified impact
3. **Top Contributor:** Best performing position (stock or bond) with market context explaining why
4. **Key Detractor:** Worst performing position with contextual explanation
5. **Secondary Themes:** Additional meaningful drivers (could include issuer-level bond analysis)
6. **Interest Rate/Credit Context:** For bond-heavy portfolios, mention duration/credit impact
7. **Summary:** Aggregate impact of top contributors across asset classes

**Quality Standards:**
- Maximum 10 sentences
- Include specific percentages and dollar impacts
- Integrate market context naturally for both stocks and bonds
- **For bonds:** Reference issuer-level news rather than individual bond specifics
- Use professional language suitable for client presentation
- Ensure all claims are factually supported

### 4. Suggested Technical Implementation

```python
class PortfolioNarrativeGenerator:
    def __init__(self, data_path: str)
    def load_portfolio_data(self) -> pd.DataFrame
    def classify_securities(self) -> Dict  # Separate stocks from bonds
    def calculate_performance_attribution(self) -> Dict
    def analyze_bond_issuers(self) -> Dict  # Group bonds by issuer
    def identify_key_drivers(self) -> List[Dict]  # Cross-asset class drivers
    
    # RAG Implementation Components
    def retrieve_market_context(self, drivers: List) -> Dict  # Retrieval phase
    def validate_retrieved_sources(self, context: Dict) -> Dict  # Source validation
    def generate_grounded_narrative(self, portfolio_data: Dict, context: Dict) -> str  # Augmented generation
    def add_source_attribution(self, narrative: str, sources: Dict) -> str  # Citation system
    
    def validate_narrative(self) -> Dict
    def export_results(self) -> None
```

---

## Expected Output

### Sample Enhanced Narrative

*"The portfolio gained 2.8% during the period from September 30 to October 24, 2025, with 9 positions advancing and 5 declining. Industrial holdings were the primary theme, driving gains with a 2.1% contribution to returns from 29.1% of portfolio exposure. Caterpillar Inc. (CAT) was the top contributor, advancing 9.9% and adding 2.1% to portfolio returns as the stock gained momentum following its October 12th announcement of acquiring RPMGlobal, an Australian mining software firm, for $728 million, signaling Caterpillar's strategic shift into digital mining solutions. The strategic move into digital mining solutions was well-received by investors, with CAT gaining 2.4% in premarket trading and closing up 2.7% on the announcement day. Home Depot Inc. (HD) was the largest detractor, declining 4.6% and reducing returns by 1.1% as the stock faced pressure amid concerns about consumer discretionary spending and housing market conditions. Information Technology positions also contributed positively, with a 0.6% impact on overall results led by IBM's strong 9.0% advance. The top three performing positions collectively contributed 2.8% to portfolio performance, demonstrating strong stock selection during a period of mixed market themes."*

### Supporting Analytics Tables

**Portfolio Summary:**
- Total Return
- Equity Contribution
- Fixed Income Contribution
- Best Contributor
- Worst Contributor
- Winning Positions

**Asset Class Attribution:**
- Equities
- Government Bonds
- Corporate Bonds

**Sector/Issuer Attribution:**
- Industrials (Equity)
- US Treasury (Bonds)
- Information Technology
- Bank of America (Issuer)
- Consumer Discretionary

---

## Evaluation Criteria

### Technical Excellence (25%)
- **Code Quality:** Clean, documented, maintainable implementation
- **Accuracy:** Correct financial calculations and attribution analysis
- **Architecture:** Well-structured classes and methods
- **Error Handling:** Robust data validation and exception management

### RAG Implementation Quality (30%)
- **Retrieval System:** Effective search and information gathering from external sources
- **Source Validation:** Proper verification of retrieved information accuracy and relevance
- **Grounding:** All generated content appropriately tied to portfolio data or retrieved context
- **Attribution System:** Clear citation of sources for all factual claims
- **Hallucination Prevention:** No speculative content beyond available data/sources
- **Confidence Scoring:** Appropriate assessment of information reliability

### Market Context Integration (20%)
- **Equity Analysis:** Identification of material corporate events explaining stock performance
- **Bond Analysis:** Appropriate use of issuer-level research rather than individual bond focus
- **Cross-Asset Context:** Understanding of interest rate environment, credit conditions
- **Source Quality:** Use of credible financial news sources for both equity and credit markets

### Narrative Quality (15%)
- **Clarity:** Professional writing suitable for executive consumption
- **Completeness:** Coverage of key performance drivers within sentence limit
- **Factual Support:** All claims backed by quantitative evidence or cited sources
- **Business Relevance:** Practical insights useful for portfolio management

### Innovation & Insight (10%)
- **Analytical Depth:** Identification of non-obvious themes or relationships
- **Production Readiness:** Consideration of automated deployment
- **Business Understanding:** Demonstration of portfolio management knowledge

---

## Deliverables

### 1. Python Implementation
**File:** `portfolio_narrative_analyzer.py`
- Complete working implementation with RAG methodology
- Comprehensive docstrings and comments
- Example usage and testing code

### 2. Generated Narrative
**File:** `portfolio_narrative.txt`
- Final 10-sentence performance narrative with source citations
- Supporting quantitative evidence
- Source attribution summary

### 3. RAG Implementation Documentation
**File:** `rag_methodology.md`
- Explanation of retrieval strategy and sources used
- Source validation and confidence scoring methodology
- Attribution system implementation details
- Approach for preventing hallucinations

### 4. Analysis Summary
**File:** `analysis_summary.xlsx` or `.csv`
- Portfolio summary metrics
- Position-level attribution table
- Sector analysis breakdown
- Market context research notes with source URLs

### 5. Documentation
**File:** `README.md`
- Methodology explanation including RAG implementation
- Usage instructions
- Data sources and assumptions
- Production deployment considerations

---

## Presentation Format

**Duration:** 30 minutes

### Technical Demo (15 minutes)
- Code walkthrough highlighting key functionality
- Data processing and calculation methodology
- Web search implementation and context integration
- Validation and quality assurance approach

### Results Discussion (10 minutes)
- Present generated narrative and supporting analysis
- Explain key themes identified and their market context
- Discuss validation of factual claims and sources
- Address any data quality issues or limitations

### Production Considerations (5 minutes)
- Approach for daily automated portfolio reporting
- Data infrastructure and monitoring requirements
- Quality controls and approval workflow
- Scalability for multiple portfolios and time periods

---

## Success Indicators

**Note:** This assignment reflects real-world portfolio reporting challenges where accuracy, timeliness, and clear communication are critical for investment management success.

### Recommended News Sources
- **Equity Research:** Bloomberg, Reuters, Wall Street Journal, company press releases, SEC filings
- **Fixed Income/Credit:** Bloomberg Credit, Moody's, S&P Global Ratings, Federal Reserve communications
- **General Financial:** Financial news aggregators (Yahoo Finance, MarketWatch)
- **Sector-Specific:** Industry publications for both equity and credit analysis
- **Economic Data:** Treasury.gov, Federal Reserve Economic Data (FRED)

### Technical Guidelines
- Use proper exception handling for web requests
- Implement rate limiting for API calls
- Cache search results to avoid redundant requests
- Validate all financial calculations with cross-checks
- **RAG Implementation:** Ensure clear separation between retrieval and generation phases
- **Source Validation:** Implement confidence scoring for all retrieved information
- **Attribution System:** Maintain clear mapping between claims and sources
- **Hallucination Prevention:** Never generate content not grounded in data or sources

### Business Context
- **Equity Focus:** Corporate actions, earnings, strategic announcements
- **Bond Focus:** Credit events, rating changes, issuer financial health, duration impact
- Prioritize issuer-level analysis over individual bond performance
- Consider interest rate environment impact on fixed income allocation
- Think from a client presentation perspective across asset classes

**Note:** This assignment reflects real-world portfolio reporting challenges where accuracy, timeliness, and clear communication are critical for investment management success.
