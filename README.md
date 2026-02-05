# Ops Assistant - Indoor Location Query Chatbot

A natural language CLI chatbot that answers questions about indoor location data by generating and executing SQL queries against a SQLite database.

## Features

- **Natural Language Queries**: Ask questions in plain English
- **Time Window Support**: Query data from today, yesterday, last X minutes/hours/days
- **Dwell Time Analysis**: Find how long entities spent in zones
- **Zone Occupancy**: See who is/was in specific zones
- **Movement Tracking**: Track entity movement between zones
- **Data Quality Checks**: Detect floor jumps and low RSSI readings
- **SQL Transparency**: Shows the SQL query used for each answer

## Database Schema

The system uses four main tables:

### 1. Zones
Physical areas in the building (rooms, corridors, etc.)
- `zone_ID`: Unique identifier (e.g., Z1-101)
- `zone_name`: Human-readable name
- `floor`: Floor number
- `zone_type`: Type (office, corridor, meeting_room, etc.)
- `description`: Optional description

### 2. Entities
People or assets being tracked
- `entity_ID`: Unique identifier (E001, A001, etc.)
- `entity_name`: Name of person or asset
- `entity_type`: Type (person, equipment, etc.)
- `department`: Associated department
- `active`: Whether entity is active

### 3. Pings
Raw location measurements from positioning system
- `ping_ID`: Auto-increment ID
- `entity_ID`: Reference to entity
- `zone_ID`: Where the entity was detected
- `timestamp`: When the ping occurred
- `rssi`: Signal strength (typically -30 to -90 dBm)
- `accuracy_meters`: Position accuracy

### 4. Zone Events
Derived events showing zone entry/exit
- `event_ID`: Auto-increment ID
- `entity_ID`: Reference to entity
- `zone_ID`: Zone entered or exited
- `event_type`: 'enter' or 'exit'
- `timestamp`: When the event occurred
- `dwell_seconds`: Time spent in zone (for exit events)

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- SQLite3 (included with Python)

### Installation

1. **Clone or download the project files**:
   - `schema.sql` - Database schema definition
   - `generate_sample_data.py` - Sample data generator
   - `ops_assistant.py` - Main chatbot application
   - `README.md` - This file

2. **Generate Sample Data**:
   ```bash
   python generate_sample_data.py
   ```
   
   This creates `location_data.db` with:
   - 14 zones across 3 floors
   - 10 entities (7 people, 3 assets)
   - ~48 hours of realistic location data
   - Intentional data quality issues for testing

3. **Run the Ops Assistant**:
   ```bash
   python ops_assistant.py
   ```

## Usage Examples

### Time Window Queries

**Today's activity**:
```
Query: How long did Alice spend in the Engineering Office today?
```

**Yesterday's data**:
```
Query: Who was in the meeting room yesterday?
```

**Recent activity**:
```
Query: Show me Bob's movement in the last 2 hours
Query: Who was in the lab in the last 30 minutes?
```

### Dwell Time Queries

```
Query: How long did Carol spend in the break room today?
Query: Who spent the most time in the sales office yesterday?
```

### Zone Occupancy

**Current location**:
```
Query: Who is in the lab?
Query: Where is Alice?
```

**Historical occupancy**:
```
Query: Who was in Conference Room A yesterday?
Query: Show everyone who was in the lobby today
```

### Movement Tracking

```
Query: Show me Alice's movement today
Query: Where did Bob go in the last hour?
Query: Track Carol's path yesterday
```

### Data Quality Checks

**Floor jumps** (entities appearing on different floors too quickly):
```
Query: Check for floor jumps
Query: Find floor jumps in the last 30 minutes
```

**Low signal strength**:
```
Query: Find low RSSI readings
Query: Show bad signal quality today
```

### Information Queries

```
Query: List all zones
Query: Show all entities
```

## Query Capabilities

### Supported

1. **Time windows**: today, yesterday, last X minutes/hours/days
2. **Dwell time**: Total time spent in zones
3. **Zone occupancy**: Current and historical
4. **Entity location**: Current and historical
5. **Movement patterns**: Tracking paths between zones
6. **Data quality**: Floor jumps, low RSSI detection
7. **Basic info**: List zones and entities

### Limitations

The assistant will inform you if:
- No data exists for the specified time period
- Entity or zone names aren't recognized
- The query type isn't supported
- The query is too ambiguous to generate SQL

## Sample Data Details

The generated sample data includes:

**Zones** (14 total):
- Floor 1: Lobby, Reception, Conference Room A, Corridor, Break Room
- Floor 2: Engineering Office, Sales Office, Meeting Room B, Corridor, Lab
- Floor 3: Executive Office, Board Room, Corridor, Storage

**Entities**:
- People: Alice Johnson, Bob Smith, Carol Davis, David Brown, Eve Wilson, Frank Miller, Grace Lee
- Equipment: Projector Cart 1, Laptop Cart, Test Device Alpha

**Data Characteristics**:
- ~48 hours of data (2 days)
- Realistic daily patterns (7 AM - 7 PM)
- Lunch breaks in break room
- Department-based office assignments
- Occasional meetings
- Injected data quality issues:
  - Floor jumps (rapid floor changes)
  - Low RSSI readings (< -75 dBm)

## Architecture

### Query Processing Pipeline

1. **Classification**: Determine query type (dwell_time, who_in_zone, movement, etc.)
2. **Time Parsing**: Extract time windows from natural language
3. **Entity/Zone Extraction**: Identify relevant entities and zones
4. **SQL Generation**: Build SQL query based on classification and extracted info
5. **Execution**: Run query against SQLite database
6. **Formatting**: Convert results to human-readable answer

### Key Components

**`OpsAssistant` class**:
- `parse_time_window()`: Convert "today", "last 30 minutes" to timestamps
- `classify_query()`: Determine what the user is asking
- `generate_sql()`: Build appropriate SQL query
- `execute_query()`: Run SQL and return results
- `format_answer()`: Convert SQL results to natural language
- `process_query()`: Main pipeline orchestrator

## Extending the System

### Adding New Query Types

1. Add classification logic in `classify_query()`
2. Implement SQL generation in `generate_sql()`
3. Add formatting logic in `format_answer()`

### Adding New Entities/Zones

Modify `generate_sample_data.py` or insert directly:

```python
# Add a new zone
conn.execute("""
    INSERT INTO zones VALUES 
    ('Z2-206', 'Server Room', 2, 'technical', 'Data center')
""")

# Add a new entity
conn.execute("""
    INSERT INTO entities VALUES 
    ('E008', 'Henry Adams', 'person', 'IT', 1)
""")
```

### Custom Data Quality Checks

Add new checks in the `data_quality` section of `generate_sql()`:

```python
elif 'custom_check' in query.lower():
    sql = """
    -- Your custom SQL here
    """
    return sql
```

## Troubleshooting

**"Could not connect to database"**:
- Run `python generate_sample_data.py` first
- Ensure `location_data.db` exists in the same directory

**"No data found matching your query"**:
- Check entity/zone names (use "list all zones" or "show all entities")
- Verify time window (data only covers ~48 hours)
- Try a broader query

**"I couldn't generate a query for that"**:
- Include specific entity or zone names
- Use supported query patterns (see Usage Examples)
- Type "help" for examples

## API Alternative

To use as a Python API instead of CLI:

```python
from ops_assistant import OpsAssistant

# Initialize
assistant = OpsAssistant('location_data.db')

# Process query
sql, answer = assistant.process_query("Where is Alice?")

print(f"SQL: {sql}")
print(f"Answer: {answer}")

# Close connection
assistant.close()
```

## Testing

Run these test queries after setup:

```bash
python ops_assistant.py
```

Then try:
1. `help` - See all examples
2. `list all zones` - Verify zones loaded
3. `show all entities` - Verify entities loaded
4. `where is alice?` - Test entity location
5. `check for floor jumps` - Test data quality
6. `how long did bob spend in engineering today?` - Test dwell time
7. `who was in the lab yesterday?` - Test zone occupancy

