# Build the Docker image
build:
	docker build -t budget-analysis .


# Run the analysis script
run-analysis:
	docker run --rm -v $(PWD)/output:/app/output budget-analysis python3 analysis.py

# Run the budgetnavn script
run-budgetnavn:
	docker run --rm -v $(PWD)/output:/app/output budget-analysis python3 budget_by_Budgetartnavn.py && \
	docker run --rm -v $(PWD)/output:/app/output budget-analysis python3 financial_by_Budgetartnavn.py

# Run the overlap check script
run-overlap:
	docker run --rm -v $(PWD)/output:/app/output budget-analysis python3 overlap_check.py

run-overview:
   docker run --rm -v $(PWD)/output:/app/output budget-analysis python3 overview.py


# Run both scripts
run-all:
	docker run --rm -v $(PWD)/output:/app/output budget-analysis python3 analysis.py && \
	docker run --rm -v $(PWD)/output:/app/output budget-analysis python3 budget_by_Budgetartnavn.py && \
	docker run --rm -v $(PWD)/output:/app/output budget-analysis python3 overview.py && \
	docker run --rm -v $(PWD)/output:/app/output budget-analysis python3 overlap_check.py

# Clean the output directory
clean:
	rm -rf output/*
