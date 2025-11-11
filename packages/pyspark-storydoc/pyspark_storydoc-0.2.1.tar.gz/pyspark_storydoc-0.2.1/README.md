# PySpark StoryDoc

> Transform your PySpark data pipelines into business-friendly documentation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PySpark](https://img.shields.io/badge/pyspark-3.5+-orange.svg)](https://spark.apache.org/)
[![License: CC-BY-NC-SA-4.0](https://img.shields.io/badge/License-CC--BY--NC--SA--4.0-green.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## What is PySpark StoryDoc?

PySpark StoryDoc automatically generates clear, business-friendly documentation from your PySpark data pipelines. Track data lineage, capture business context, and create visual documentation that stakeholders can understand.

## Key Capabilities

**Automatic Lineage Tracking**
- Track data transformations without manual documentation
- Capture business logic and decision points
- Monitor data quality metrics (row counts, filtering impact)
- Column-level tracking and expression lineage

**One-Line Report Generation**
- Generate any report with a single method call
- Discoverable via IDE autocomplete (`df.generate_*`)
- Smart defaults and automatic path handling
- No internal imports required

**Multi-Audience Reporting**
- Executive View: High-level business impact and data flow
- Business Analyst View: Detailed logic with metrics and filters
- Technical View: Complete operation-level debugging information

**Governance & Compliance**
- Comprehensive governance metadata
- Risk assessment and mitigation tracking
- Customer impact analysis
- PII and data classification
- Approval workflows

## Quick Start

### Installation

```bash
pip install pyspark-storydoc
```

**Databricks Installation**

When installing on Databricks or other managed Spark environments where PySpark is pre-installed:

```bash
pip install pyspark-storydoc --no-deps
```

This prevents pip from attempting to install a different PySpark version and uses your existing Spark installation.

### Basic Example

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark_storydoc import LineageDataFrame, businessConcept

# Initialize Spark
spark = SparkSession.builder.appName("MyApp").getOrCreate()

# Create sample data
customers_data = [
    (1, "Alice", "Premium", 1500),
    (2, "Bob", "Standard", 800),
    (3, "Charlie", "Premium", 2000),
]
customers = spark.createDataFrame(
    customers_data,
    ["customer_id", "name", "tier", "spend"]
)

# Wrap DataFrame to enable tracking
customers_ldf = LineageDataFrame(customers, business_label="Customer Data")

# Define business logic with decorator
@businessConcept(
    name="Filter High-Value Customers",
    description="Identify customers with spending above $1000"
)
def filter_high_value_customers(df):
    return df.filter(col("spend") > 1000)

# Execute and generate documentation
high_value = filter_high_value_customers(customers_ldf)
diagram_path = high_value.generate_business_flow_diagram()
```

## Available Reports

All reports accessible via simple `df.generate_*()` method calls:

### Business Stakeholder Reports
- `generate_business_catalog()` - Business concept catalog with descriptions and metrics
- `generate_business_flow_diagram()` - Visual Mermaid flowchart of pipeline
- `generate_concept_relationship_diagram()` - Concept dependencies and relationships

### Data Engineer Reports
- `generate_data_engineer_report()` - Technical debugging with row counts and data loss detection
- `generate_comprehensive_tracking_report()` - Multi-view combined report

### Data Science Reports
- `generate_feature_catalog()` - Complete feature documentation with lineage
- `generate_statistical_profile()` - Statistical profiling with checkpoints
- `generate_distribution_report()` - Distribution analysis and value frequencies
- `generate_describe_profiler_report()` - PySpark describe() statistics

### Governance Reports
- `generate_governance_audit_report()` - Comprehensive governance audit for compliance
- `generate_governance_report()` - Full governance documentation with risk assessment
- `generate_governance_catalog()` - Text format governance metadata catalog
- `generate_integrated_governance_report()` - Lineage with governance overlay

### Technical Reports
- `export_lineage_json()` - JSON export for external tools
- `generate_expression_documentation()` - Expression lineage documentation
- `generate_expression_impact_diagram()` - Expression dependency visualization

## Core Features

### Business Concept Tracking

Group related operations under meaningful business concepts:

```python
@businessConcept(
    name="Premium Customer Identification",
    description="Identify high-value customers for targeted campaigns"
)
def identify_premium_customers(df):
    high_value = df.filter(col("lifetime_value") > 25000)
    active = high_value.filter(col("status") == "active")
    return active.filter(col("engagement_score") > 0.8)
```

### Context Managers

Use context managers for inline grouping:

```python
from pyspark_storydoc import business_context

with business_context("Geographic Segmentation"):
    na_customers = df.filter(col("region") == "North America")
    enriched = na_customers.join(demographics, "customer_id")
    segmented = enriched.groupBy("state", "age_group").count()
```

### Distribution Analysis

Automatically analyze data distributions and value frequencies:

```python
from pyspark_storydoc import distributionAnalysis

@distributionAnalysis(
    name="Customer Tier Analysis",
    analyze_columns=["tier", "region"]
)
def segment_customers(df):
    return df.groupBy("tier", "region").agg(
        count("*").alias("customer_count"),
        avg("spend").alias("avg_spend")
    )
```

### Hierarchical Concepts

Build nested business concepts for complex pipelines:

```python
from pyspark_storydoc import HierarchyContext

with HierarchyContext("Insurance Quote Calculation"):
    with HierarchyContext("Risk Assessment"):
        risk_df = calculate_risk_scores(driver_data)

    with HierarchyContext("Premium Calculation"):
        premium_df = calculate_premiums(risk_df, policy_data)
```

## Governance Framework

### Quick Governance Example

```python
from pyspark_storydoc.governance import create_quick_governance

@businessConcept(
    "Calculate Insurance Premium",
    description="Calculate customer premium based on risk assessment",
    governance=create_quick_governance(
        why="Required for automated underwriting and pricing",
        risks=["Potential algorithmic bias in risk scoring"],
        mitigations=["Quarterly fairness audits by third party"],
        impacts_customers=True,
        impacting_columns=["premium", "risk_score"]
    )
)
def calculate_premium(df):
    return df.withColumn("premium", col("base_rate") + (col("risk_score") * 5))
```

### Governance Features

**Risk Assessment**
- Track known risks and mitigation strategies
- Automatic risk detection
- Severity classification

**Customer Impact Tracking**
- Identify operations that directly affect customers
- Document impacting columns
- Impact level classification (direct/indirect/none)

**PII and Data Classification**
- Track sensitive data handling
- Data retention policies
- Classification levels

**Approval Workflows**
- Document approval requirements
- Track approval status and approvers
- Reference tickets and dates

## Examples

### Basic Examples
- `01_business_concept_decorator.py` - Basic decorator usage
- `02_business_concept_context.py` - Context manager usage
- `05_lineage_tracking_decorator.py` - Full lineage tracking

### Advanced Examples
- `car_insurance_quote_example.py` - Complete insurance quote pipeline
- `car_insurance_with_governance.py` - Full governance framework
- `streaming_service_analysis.py` - Video streaming analytics

### Data Engineer Examples
- `simple_debugging_example.py` - Pipeline debugging with semantic shapes
- `customer_enrichment_pipeline.py` - Large-scale pipeline with quality alerts

### Data Scientist Examples
- `customer_churn_features.py` - Feature engineering with business context
- `feature_evolution_demo.py` - Feature evolution tracking

### Running Examples

```bash
# Clone the repository
git clone https://github.com/kaelonlloyd/pyspark_storydoc.git
cd pyspark_storydoc

# Run any example
python examples/basic/01_business_concept_decorator.py
python examples/advanced/car_insurance_quote_example.py

# View generated outputs
ls outputs/examples/
```

## Performance Configuration

### Control Materialization

```python
from pyspark_storydoc.core.lineage_tracker import get_global_tracker

# Global settings
tracker = get_global_tracker()
tracker.set_global_materialize(False)  # Disable expensive metrics

# Per-concept settings
@businessConcept(
    name="Large Dataset Processing",
    materialize=False,  # Skip row counting
    auto_cache=True     # Enable smart caching
)
def process_large_dataset(df):
    return df.filter(complex_condition)
```

### Smart Caching

```python
# Automatic caching for reused DataFrames
df = LineageDataFrame(
    spark_df,
    auto_cache=True,
    cache_threshold=2  # Cache after 2 uses
)
```

## Use Cases

**Stakeholder Communication**
Generate executive-friendly reports showing how raw data becomes business insights.

**Data Governance**
Maintain audit trails with automatic lineage capture and business context.

**Pipeline Optimization**
Identify bottlenecks by visualizing where data volume changes occur.

**Knowledge Transfer**
Document complex pipelines for team onboarding and handoffs.

**Compliance Reporting**
Track data transformations with detailed context for regulatory requirements.

## Documentation Output

### Detail Levels
- `minimal`: Only business concepts and key transformations
- `impacting`: Operations that change data volume or structure (default)
- `all`: Every operation including passthroughs

### Output Formats
- Markdown with Mermaid diagrams (GitHub-compatible)
- JSON for programmatic access
- Statistical profiling reports

## Testing

```bash
# Run all tests
python run_all_tests.py

# Run specific test categories
python run_all_tests.py --unit
python run_all_tests.py --integration

# Run with verbose output
python run_all_tests.py --verbose
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/kaelonlloyd/pyspark_storydoc.git
cd pyspark_storydoc
pip install -r requirements.txt
python run_all_tests.py
```

## License

This project is licensed under CC-BY-NC-SA-4.0 - see the [LICENSE](LICENSE) file for details.

---

## Get Started

```bash
pip install pyspark-storydoc
python examples/basic/01_business_concept_decorator.py
```

**Questions?** [Open an issue](https://github.com/kaelonlloyd/pyspark_storydoc/issues) or [start a discussion](https://github.com/kaelonlloyd/pyspark_storydoc/discussions)
