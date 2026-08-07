<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Curriculum Practices Navigator</title>
    <style>
        :root {
            --primary-color: #005a9c;
            --bg-color: #f4f7f9;
            --card-bg: #ffffff;
            --text-color: #333333;
            --border-color: #cccccc;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }

        .container {
            width: 100%;
            max-width: 900px;
            background: var(--card-bg);
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        h1 {
            color: var(--primary-color);
            margin-top: 0;
            margin-bottom: 24px;
            font-size: 1.8rem;
        }

        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        label {
            font-weight: 600;
            margin-bottom: 6px;
            font-size: 0.9rem;
        }

        select {
            padding: 10px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 0.95rem;
            background-color: #fff;
            outline: none;
            transition: border-color 0.2s;
        }

        select:focus {
            border-color: var(--primary-color);
        }

        select:disabled {
            background-color: #e9ecef;
            cursor: not-allowed;
        }

        .output-box {
            border-top: 2px solid var(--primary-color);
            padding-top: 20px;
            margin-top: 10px;
        }

        .output-box h2 {
            font-size: 1.3rem;
            color: var(--primary-color);
            margin-top: 0;
        }

        ul {
            padding-left: 20px;
            line-height: 1.6;
        }

        li {
            margin-bottom: 10px;
        }

        .empty-state {
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Mathematics Practices Navigator</h1>

    <div class="controls">
        <div class="form-group">
            <label for="phaseSelect">1. Phase</label>
            <select id="phaseSelect">
                <option value="">Select Phase</option>
                <option value="Phase 1">Phase 1 (Years 1–3)</option>
                <option value="Phase 2">Phase 2 (Years 4–6)</option>
                <option value="Phase 3">Phase 3 (Years 7–8)</option>
            </select>
        </div>

        <div class="form-group">
            <label for="yearSelect">2. Year Level</label>
            <select id="yearSelect" disabled>
                <option value="">Select Year</option>
            </select>
        </div>

        <div class="form-group">
            <label for="strandSelect">3. Strand</label>
            <select id="strandSelect" disabled>
                <option value="">Select Strand</option>
            </select>
        </div>

        <div class="form-group">
            <label for="subStrandSelect">4. Sub-Strand</label>
            <select id="subStrandSelect" disabled>
                <option value="">Select Sub-Strand</option>
            </select>
        </div>
    </div>

    <div class="output-box" id="outputBox">
        <p class="empty-state">Please select a Phase, Year Level, Strand, and Sub-Strand to view the target Practices.</p>
    </div>
</div>

<script>
const curriculumData = {
    "Phase 2": {
        "Year 4": {
            "Number": {
                "Number Structures": [
                    "Read, write, compare, order, and represent numbers up to 10,000.",
                    "Round whole numbers to the nearest 10, 100, or 1,000, and round tenths to the nearest whole number.",
                    "Count in 2s, 3s, 4s, 5s, 6s, 7s, 8s, 9s, 25s, and 50s from multiples, and in 10s, 100s, and 1,000s from any whole number up to 10,000."
                ],
                "Operations": [
                    "Add and subtract numbers up to four digits.",
                    "Memorise multiplication and division facts from 2s to 10s.",
                    "Multiply 2- and 3-digit numbers by a 1-digit number.",
                    "Divide up to 3-digit numbers by a 1-digit divisor with no remainder."
                ],
                "Rational Numbers": [
                    "Read, write, compare, and order tenths as fractions and decimals.",
                    "Multiply and divide whole numbers by 10 to work with decimal tenths.",
                    "Memorise the decimal equivalent of 1/2 (0.5) and tenths.",
                    "Add and subtract fractions with common denominators and decimals to one decimal place.",
                    "Find a unit fraction of a whole number and find the whole from a fractional part."
                ],
                "Financial Mathematics": [
                    "Calculate total costs and change for dollar amounts.",
                    "Represent money values using different combinations of coins and notes."
                ]
            },
            "Algebra": {
                "Equations and Relationships": [
                    "Check the truth of and solve open equations involving addition, subtraction, multiplication, or division.",
                    "Identify, extend, and create growing numerical and non-numerical patterns."
                ]
            },
            "Measurement": {
                "Measuring": [
                    "Measure length, mass, and capacity in mixed metric units and temperature in degrees Celsius.",
                    "Calculate perimeter of polygons and areas of rectangles/squares using side length multiplication.",
                    "Measure irregular shape areas using grid squares and 3D volume using unit blocks.",
                    "Tell time to the exact minute on analogue/digital clocks and convert equivalent durations."
                ]
            },
            "Geometry": {
                "Shapes & Spatial Reasoning": [
                    "Classify polygons up to 12 sides using edges, vertices, and angles.",
                    "Identify lines of symmetry and connect 3D shapes to 2D perspective diagrams.",
                    "Perform one-step reflections, translations, and rotations on 2D shapes."
                ],
                "Pathways": [
                    "Use alphanumeric grid references to plot positions and locate regions on maps."
                ]
            },
            "Statistics": {
                "Developing Knowledge & Visualisation": [
                    "Collect numerical data and create dot plots or bar graphs."
                ],
                "Interpretation of Data": [
                    "Answer questions using dot plots and bar graphs by distinguishing between specific data values and overall frequencies."
                ]
            }
        },
        "Year 5": {
            "Number": {
                "Number Structures": [
                    "Reading, writing, comparing, and ordering whole numbers up to 1,000,000 and representing them using base 10 structure.",
                    "Finding factor pairs for numbers that result from multiplying any two whole numbers between 1 and 10.",
                    "Rounding whole numbers to the nearest hundred thousand, ten thousand, thousand, hundred, or ten.",
                    "Rounding tenths or hundredths to the nearest whole number.",
                    "Counting forwards and backwards in 11s and 12s from multiples of the counting unit.",
                    "Counting in 1,000s, 10,000s, and 100,000s from any whole number up to 100,000.",
                    "Counting backwards through 0 to include negative whole numbers."
                ],
                "Operations": [
                    "Adding and subtracting increasingly large whole numbers.",
                    "Memorising multiplication and corresponding division facts for 2s to 12s.",
                    "Applying mental strategies, number facts, derived facts, factor pairs, and multiples to multiply and divide increasingly large numbers.",
                    "Multiplying three-digit and four-digit numbers by a one-digit number and multiplying two two-digit numbers.",
                    "Dividing up to four-digit whole numbers by a one-digit divisor, with a remainder."
                ],
                "Rational Numbers": [
                    "Reading, writing, and representing tenths and hundredths as fractions and decimals.",
                    "Comparing tenths or hundredths as fractions and decimals.",
                    "Comparing and ordering numbers with up to two decimal places.",
                    "Memorising and using decimal equivalents of 1/2, 1/4, 3/4, and fractions with denominators of 10 or 100.",
                    "Converting common percentages (10%, 25%, 50%) to fractions and decimals.",
                    "Dividing one- and two-digit whole numbers by 10 or 100 to make decimals and identify tenths and hundredths places.",
                    "Multiplying numbers with up to two decimal places by 10 and 100.",
                    "Comparing fractions where one denominator is a multiple of the other.",
                    "Recognising families of equivalent fractions.",
                    "Recognising equivalent mixed numbers and improper fractions.",
                    "Adding and subtracting fractions with the same denominator or when one denominator is a multiple of the other, including improper fractions.",
                    "Adding and subtracting decimals to two decimal places.",
                    "Finding a non-unit fraction of a whole number, using multiplication and division facts.",
                    "Finding a whole set from a fractional part of the set.",
                    "Finding common percentages (10%, 25%, 50%) of whole numbers.",
                    "Finding the whole (100%) when given 25% or 50%."
                ],
                "Financial Mathematics": [
                    "Calculating the total cost of items costing dollars and cents and the change from the nearest ten dollars.",
                    "Representing currency values of mixed dollars and cents using decimal notation.",
                    "Rounding dollar amounts to the nearest dollar."
                ]
            },
            "Algebra": {
                "Equations and Relationships": [
                    "Completing number sentences that involve addition and subtraction by using equality (=) and inequality (<, >) symbols.",
                    "Checking the truth of number sentences and completing open number sentences.",
                    "Recognising, continuing, creating, and describing growing patterns that change by a constant amount."
                ]
            },
            "Measurement": {
                "Measuring": [
                    "Accurately measuring length with a ruler, mass with scales, capacity with measuring jugs, temperature with a thermometer, and duration with a timer.",
                    "Converting metric units of length (m and cm).",
                    "Approximating the areas of irregular shapes covered with squares, half squares, and partial squares.",
                    "Calculating the areas of rectangles (including squares) using multiplication of side lengths.",
                    "Measuring the volumes of rectangular prisms filled with centicubes.",
                    "Calculating the perimeters of regular polygons and other 2D shapes with straight sides.",
                    "Recognising that shapes with the same area can have different perimeters, and vice versa.",
                    "Describing and classifying angles and turns using acute, right, obtuse, straight, and reflex.",
                    "Classifying and constructing angles up to 180°, using a protractor.",
                    "Telling the time on analogue and digital clocks.",
                    "Finding the duration of periods of time involving a.m. and p.m. notation and 24-hour time."
                ]
            },
            "Geometry": {
                "Shapes & Spatial Reasoning": [
                    "Identifying, classifying, and describing the attributes of prisms, using cross sections, faces, edges, and vertices.",
                    "Identifying parallel and perpendicular lines, including those forming the sides of polygons.",
                    "Connecting 3D shapes with nets.",
                    "Describing the transformations performed (reflections, translations, rotations) on 2D shapes."
                ],
                "Pathways": [
                    "Interpret and create grid maps to plot positions and pathways, using grid references and directional language, including the four main compass points."
                ]
            },
            "Statistics": {
                "Developing Knowledge & Visualisation": [
                    "Collecting continuous numerical data by taking measurements, and then applying specified rounding rules.",
                    "Collecting bivariate data with two categorical variables.",
                    "Creating tables for continuous numerical data, using groupings.",
                    "Creating clustered bar graphs for paired categorical data."
                ],
                "Interpretation of Data": [
                    "Answering questions about the frequency of particular values or groups of values from a table for continuous numerical data.",
                    "Answering questions about bivariate data.",
                    "Interpreting data visualisations."
                ]
            },
            "Probability": {
                "Experimental Probability": [
                    "Conducting repeated chance experiments or games, identifying outcomes, and describing differences using likelihood vocabulary.",
                    "Identifying the likelihood of an everyday event as impossible, unlikely, even-chance, likely, or certain.",
                    "Placing everyday events on a number line according to their likelihood."
                ]
            }
        },
        "Year 6": {
            "Number": {
                "Number Structures": [
                    "Reading, writing, comparing, and ordering any whole number and representing them using base 10 structure.",
                    "Finding factor pairs for numbers resulting from multiplying whole numbers between 1 and 12.",
                    "Rounding whole numbers to the nearest million, hundred thousand, ten thousand, thousand, hundred, or ten.",
                    "Rounding hundredths to the nearest whole number or tenth.",
                    "Recognising square and cube numbers and notation for squared (2) and cubed (3).",
                    "Memorising square numbers to 144 and cube numbers to 125.",
                    "Counting forwards and backwards with positive whole numbers, including working with negative numbers."
                ],
                "Operations": [
                    "Calculating expressions using the order of operations.",
                    "Adding and subtracting any whole numbers.",
                    "Multiplying any whole number by a two-digit number.",
                    "Dividing up to five-digit whole numbers by a one-digit divisor, with a remainder.",
                    "Connecting finding unit fractions of whole numbers to division (with remainders).",
                    "Representing remainders from division as whole numbers, fractions, or rounded decimals, as appropriate."
                ],
                "Rational Numbers": [
                    "Reading, writing, and representing tenths, hundredths, and thousandths as fractions and decimals.",
                    "Comparing and ordering numbers with up to three decimal places.",
                    "Memorising decimal and percentage equivalents of common fractions.",
                    "Converting decimal tenths and hundredths to fractions and percentages.",
                    "Multiplying and dividing numbers by 10, 100, or 1,000.",
                    "Finding equivalent fractions.",
                    "Comparing and ordering fractions where at least one denominator is a common multiple.",
                    "Converting between mixed numbers and improper fractions.",
                    "Adding and subtracting fractions and mixed numbers when one denominator is a multiple of the other.",
                    "Adding and subtracting decimals to three decimal places.",
                    "Finding a non-unit fraction of a whole number.",
                    "Finding a whole set or amount when given a non-unit fraction.",
                    "Finding common percentages (1%, 10%, 20%, 25%, 50%, 75%) of whole numbers.",
                    "Finding the whole (100%) when given a percentage.",
                    "Reasoning proportionally with fractions, decimals, and percentages."
                ],
                "Financial Mathematics": [
                    "Calculating 10%, 25%, and 50% of whole dollar amounts.",
                    "Investigating questions involving purchases."
                ]
            },
            "Algebra": {
                "Equations and Relationships": [
                    "Checking the truth of and completing open number sentences involving all four operations and inequalities, respecting order of operations.",
                    "Developing a rule for a growing pattern in words and making conjectures about further elements.",
                    "Locating coordinate points on a coordinate plane, including on axes.",
                    "Generating a table of values from a rule for a growing pattern and plotting points on a coordinate plane."
                ]
            },
            "Measurement": {
                "Measuring": [
                    "Accurately measuring length, mass, capacity, temperature, and duration using metric or time-based units.",
                    "Estimating length, mass, capacity, temperature, and duration using benchmark units.",
                    "Converting metric units of length (m/cm), mass (g/kg), and capacity (L/mL) up to 2 decimal places.",
                    "Calculating, estimating, and comparing volumes of cubes and rectangular prisms in cm³ and m³.",
                    "Visualising, estimating, and calculating areas of rectangles and right-angled triangles (cm²/m²) and volume of rectangular prisms (cm³).",
                    "Classifying, measuring, and constructing angles up to 360° using a protractor.",
                    "Identifying and describing angles at a point, on a straight line, and vertically opposite angles.",
                    "Reasoning about and finding unknown angles involving angles at a point, straight lines, and vertically opposite angles.",
                    "Converting units of time (h, min, s) and measuring duration across 12- and 24-hour systems.",
                    "Finding elapsed time in minutes across an hour and using timetables."
                ]
            },
            "Geometry": {
                "Shapes & Spatial Reasoning": [
                    "Identifying, classifying, and explaining similarities and differences between 2D shapes, prisms, and pyramids.",
                    "Identifying and describing interior angles of triangles and quadrilaterals.",
                    "Identifying shapes with rotational symmetry and determining their order.",
                    "Visualising, creating, and describing 2D geometric patterns and tessellations.",
                    "Predicting results of two-step transformations on 2D shapes."
                ],
                "Pathways": [
                    "Interpret and create grid references and simple map scales, using directional language, compass points, turn, and distance."
                ]
            },
            "Statistics": {
                "Developing Knowledge & Visualisation": [
                    "Collecting time-series data.",
                    "Calculating the mean and range for numerical data.",
                    "Creating time-series graphs.",
                    "Choosing and creating appropriate data visualisations for a given dataset."
                ],
                "Interpretation of Data": [
                    "Identifying whether a time-series graph shows a trend.",
                    "Calculating an average and range for continuous numerical data.",
                    "Interpreting data visualisations, including from contemporary media."
                ]
            },
            "Probability": {
                "Experimental Probability": [
                    "Listing the sample space of an event.",
                    "Calculating probabilities of individual outcomes and spinner events.",
                    "Answering questions about probabilities of combined outcomes (checking sum equals 1)."
                ]
            }
        }
    },
    "Phase 3": {
        "Year 7": {
            "Number": {
                "Number Structures and Operations": [
                    "Reading, writing, comparing, and ordering whole numbers using powers of 10.",
                    "Representing numbers in expanded form using powers of 10.",
                    "Using exponents and identifying square roots for square numbers up to at least 144.",
                    "Using radicals (√) to represent square roots.",
                    "Using divisibility rules for 2, 3, 4, 5, 6, 8, 9, and 10.",
                    "Identifying prime numbers to 100.",
                    "Finding the highest common factor (HCF) under 100, and least common multiple (LCM) under 10.",
                    "Locating, ordering, and representing addition/subtraction of integers on a number line.",
                    "Using negative numbers to solve problems in contexts like temperature and finance.",
                    "Using rounding and estimation to check calculation reasonableness.",
                    "Rounding whole numbers to specified powers of 10, and decimals to whole, tenth, or hundredth.",
                    "Multiplying whole numbers and dividing by one- or two-digit divisors.",
                    "Evaluating expressions using the order of operations (GEMA)."
                ],
                "Rational Numbers": [
                    "Identifying, reading, writing, representing, comparing, ordering, and converting fractions, decimals, and percentages.",
                    "Finding equivalent fractions and simplifying fractions.",
                    "Adding and subtracting fractions, improper fractions, mixed numbers, and decimals.",
                    "Multiplying and dividing numbers by powers of 10.",
                    "Multiplying whole numbers by fractions, and decimals by whole numbers.",
                    "Dividing fractions by whole numbers, and whole numbers by unit fractions.",
                    "Finding fractions/percentages of whole numbers and finding whole amounts from known parts.",
                    "Using proportional reasoning to explore multiplicative relationships."
                ],
                "Financial Mathematics": [
                    "Calculating total cost and change for currency transactions.",
                    "Applying percentage discounts to whole dollar amounts."
                ]
            },
            "Algebra": {
                "Equations and Relationships": [
                    "Forming and solving one- and two-step linear equations with integer solutions.",
                    "Checking the truth of and completing number sentences involving inequalities.",
                    "Using substitution to find expression/formula values.",
                    "Rearranging known formulae using one or two steps.",
                    "Simplifying algebraic expressions by collecting like terms.",
                    "Identifying and plotting points across all four quadrants of the coordinate plane.",
                    "Using tables, graphs, and diagrams to recognize linear pattern rules and make conjectures.",
                    "Identifying constant changes in linear patterns and writing variable equations."
                ]
            },
            "Measurement": {
                "Measuring": [
                    "Selecting and using base metric measures with appropriate prefixes.",
                    "Using formulae to find unknown measurements for perimeter, area, and volume.",
                    "Reading, interpreting, and using timetables and charts presenting duration."
                ]
            },
            "Geometry": {
                "Shapes & Spatial Reasoning": [
                    "Classifying triangles by both angle and side properties.",
                    "Transforming 2D shapes in the coordinate plane by single translation, reflection, or rotation (multiples of 90°).",
                    "Identifying 2D shapes that compose 3D shapes and drawing nets for prisms and pyramids.",
                    "Reasoning about unknown angles involving perpendicular/parallel lines and transversals.",
                    "Solving multi-step equations for unknown angles using supplementary, complementary, vertical, and adjacent rules."
                ],
                "Pathways": [
                    "Interpreting and communicating locations and pathways using coordinates, angle measures, and 8 main compass points."
                ]
            },
            "Statistics": {
                "Developing Knowledge & Visualisation": [
                    "Planning and collecting data to respond to statistical questions.",
                    "Calculating mean, median, mode, and range for numerical data.",
                    "Choosing and constructing appropriate visualisations (dot plot, bar graph, time-series).",
                    "Noticing and explaining outliers in datasets."
                ],
                "Interpretation of Data": [
                    "Responding to questions by calculating central tendency and range from tables/graphs.",
                    "Interpreting data visualisations from media and identifying missing/misleading information.",
                    "Identifying outliers visually and accounting for them in range calculations."
                ]
            },
            "Probability": {
                "Experimental Probability": [
                    "Carrying out chance experiments and calculating experimental probability.",
                    "Comparing experimental probability (30+ and 100+ trials) to theoretical probability to demonstrate the Law of Large Numbers."
                ],
                "Theoretical Probability": [
                    "Calculating event probabilities as decimals, fractions, and percentages.",
                    "Comparing likelihoods of events and calculating probabilities for complementary events."
                ]
            }
        },
        "Year 8": {
            "Number": {
                "Number Structures and Operations": [
                    "Reading, writing, comparing, ordering, and representing whole numbers and decimals using positive and negative powers of 10.",
                    "Representing negative powers of 10 as fractions and decimals, and vice-versa.",
                    "Using exponents, identifying cube roots up to 125 using radicals (√ and ∛), and approximating with calculators.",
                    "Representing composite numbers as products of prime factors using exponents.",
                    "Locating, comparing, ordering, and evaluating expressions with negative numbers on a number line.",
                    "Using rounding, estimation, and benchmarks to check calculation reasonableness.",
                    "Rounding whole numbers to any power of 10, and decimals to thousandths.",
                    "Multiplying and dividing whole numbers, expressing remainders as decimals or fractions.",
                    "Evaluating expressions with integers using the order of operations."
                ],
                "Rational Numbers": [
                    "Comparing, ordering, and converting between fractions, decimals, and percentages.",
                    "Multiplying whole numbers by fractions, mixed numbers, and multiplying fractions in simplest form.",
                    "Multiplying and dividing by powers of 10, and multiplying positive decimals.",
                    "Finding fractions or percentages of whole numbers and finding the 100% whole from a given part.",
                    "Identifying percentage equivalence in calculations (e.g., 45% of 20 = 20% of 45).",
                    "Dividing quantities into parts given ratios and expressing divisions as ratios."
                ],
                "Financial Mathematics": [
                    "Creating and comparing weekly, monthly, and yearly finance plans (budgets, BNPL, phone plans).",
                    "Applying percentage discounts to find new prices."
                ]
            },
            "Algebra": {
                "Equations and Relationships": [
                    "Forming and solving linear equations with rational solutions.",
                    "Forming and solving linear inequalities and representing solutions on a number line.",
                    "Using substitution, rearranging known formulae, and simplifying expressions with single brackets and like terms.",
                    "Factorising simple algebraic expressions.",
                    "Identifying and plotting points across 4 quadrants from tables and rules.",
                    "Investigating pattern sequences of triangular, square, and cube numbers on coordinate planes."
                ]
            },
            "Measurement": {
                "Measuring": [
                    "Estimating and measuring length, area, volume, capacity, mass, temperature, time, and angle using appropriate units.",
                    "Converting between metric units of area (mm² to km²), volume (mm³ to m³), and capacity (mL, L).",
                    "Calculating area of parallelograms and trapeziums.",
                    "Calculating volume of triangular prisms and composite 3D figures.",
                    "Converting time units and interpreting timetables and duration charts."
                ]
            },
            "Geometry": {
                "Shapes & Spatial Reasoning": [
                    "Identifying and describing circle parts: radius, diameter, and circumference.",
                    "Transforming 2D composite shapes on coordinate planes using translations, reflections, rotations, and scaling.",
                    "Proving triangle interior angle sums (180°) and generalising rules for interior/exterior polygon angles.",
                    "Reasoning about unknown internal and external angles of polygons."
                ],
                "Pathways": [
                    "Using map scales, compass points, distance, and turn to interpret and communicate positions and pathways."
                ]
            },
            "Statistics": {
                "Developing Knowledge & Visualisation": [
                    "Planning and collecting data, calculating mean, median, mode, and range.",
                    "Choosing and constructing appropriate data visualisations based on data type.",
                    "Noticing and explaining outliers in data."
                ],
                "Interpretation of Data": [
                    "Interpreting data visualisations (shape, center, spread, trends, media accuracy).",
                    "Identifying missing graph information and accounting for outliers in spread calculations."
                ]
            },
            "Probability": {
                "Experimental Probability": [
                    "Carrying out chance experiments (30+ and 100+ trials) to calculate experimental probability and demonstrate the Law of Large Numbers."
                ],
                "Theoretical Probability": [
                    "Calculating probabilities for events and complementary events as fractions, decimals, and percentages."
                ]
            }
        }
    }
};

const phaseSelect = document.getElementById('phaseSelect');
const yearSelect = document.getElementById('yearSelect');
const strandSelect = document.getElementById('strandSelect');
const subStrandSelect = document.getElementById('subStrandSelect');
const outputBox = document.getElementById('outputBox');

phaseSelect.addEventListener('change', () => {
    resetDropdowns([yearSelect, strandSelect, subStrandSelect]);
    const phase = phaseSelect.value;
    
    if (phase && curriculumData[phase]) {
        populateDropdown(yearSelect, Object.keys(curriculumData[phase]), "Select Year");
        yearSelect.disabled = false;
    } else if (phase === "Phase 1") {
        outputBox.innerHTML = '<p class="empty-state">Phase 1 (Years 1–3) content is currently not loaded in this module.</p>';
    }
});

yearSelect.addEventListener('change', () => {
    resetDropdowns([strandSelect, subStrandSelect]);
    const phase = phaseSelect.value;
    const year = yearSelect.value;
    
    if (year && curriculumData[phase][year]) {
        populateDropdown(strandSelect, Object.keys(curriculumData[phase][year]), "Select Strand");
        strandSelect.disabled = false;
    }
});

strandSelect.addEventListener('change', () => {
    resetDropdowns([subStrandSelect]);
    const phase = phaseSelect.value;
    const year = yearSelect.value;
    const strand = strandSelect.value;
    
    if (strand && curriculumData[phase][year][strand]) {
        populateDropdown(subStrandSelect, Object.keys(curriculumData[phase][year][strand]), "Select Sub-Strand");
        subStrandSelect.disabled = false;
    }
});

subStrandSelect.addEventListener('change', displayPractices);

function populateDropdown(selectElement, optionsArray, placeholder) {
    selectElement.innerHTML = `<option value="">${placeholder}</option>`;
    optionsArray.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = opt;
        selectElement.appendChild(option);
    });
}

function resetDropdowns(dropdownList) {
    dropdownList.forEach(select => {
        select.innerHTML = `<option value="">Select ${select.id.replace('Select', '')}</option>`;
        select.disabled = true;
    });
    outputBox.innerHTML = '<p class="empty-state">Please select a Phase, Year Level, Strand, and Sub-Strand to view the target Practices.</p>';
}

function displayPractices() {
    const phase = phaseSelect.value;
    const year = yearSelect.value;
    const strand = strandSelect.value;
    const subStrand = subStrandSelect.value;

    if (phase && year && strand && subStrand) {
        const practices = curriculumData[phase][year][strand][subStrand];
        
        if (practices && practices.length > 0) {
            let html = `<h2>${year} Practices: ${strand} — ${subStrand}</h2><ul>`;
            practices.forEach(practice => {
                html += `<li>${practice}</li>`;
            });
            html += '</ul>';
            outputBox.innerHTML = html;
        } else {
            outputBox.innerHTML = '<p class="empty-state">No practices found for this selection.</p>';
        }
    }
}
</script>

</body>
</html>
