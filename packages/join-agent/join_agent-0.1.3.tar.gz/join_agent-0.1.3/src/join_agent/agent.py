"""
Join Agent - LLM-driven intelligent data joining and relationship analysis.

This agent analyzes data tables and suggests optimal join strategies using LLM reasoning.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple

from sfn_blueprint import SFNAIHandler, MODEL_CONFIG
from pydantic import ValidationError
import sys

from .models import JoinOutput, JoinInput, clean_json_string
from .constants import PromptsClass
from .config import JoinAgentConfig

import re
import json
from typing import Any


class JoinAgent:
    """
    LLM-driven agent for intelligent data joining and relationship analysis.
    
    This agent uses LLM reasoning to Analyze table structures and identify potential join keys

    """
    
    def __init__(self, config: Optional[JoinAgentConfig] = None):
        """Initialize the Join Agent.
        Args:config: Optional FeatureCreationConfig instance. If not provided, a default will be used.
        """
        # Initialize configuration
        self.config = config or JoinAgentConfig()
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:  # Only add handlers if none exist
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Initialize sfn_blueprint components
        self.ai_handler = SFNAIHandler()
        
        self.logger.info("Join Agent initialized successfully")

    def __call__(self, inputs: JoinInput ):
        return self.execute_task(inputs)
    
    def execute_task(self, inputs):
        """operation : enum["golden_dataset","manual_data_prep"]"""
        self.operation = inputs.operation
        table_names = inputs.tables
        col_metadata = inputs.col_metadata
        primary_table = inputs.primary_table
        groupby_fields = inputs.groupby_fields
        use_case = inputs.use_case
        ml_approach = inputs.ml_approach
        domain_metadata = inputs.domain_metadata

        if self.operation not in {"golden_dataset", "manual_data_prep"}:
            raise ValueError("operation must be 'golden_dataset' or 'manual_data_prep'")

        if self.operation == "manual_data_prep" and len(table_names) > 2:
            raise ValueError("Only two tables can be analyzed when operation = 'manual_data_prep'")

        self.logger.info(f"Analyzing join keys between :{', '.join(table_names)}")
        
        
        # Generate LLM prompt for join analysis
        system_prompt, user_prompt = PromptsClass().operation_prompt(self.operation,table_names, col_metadata, primary_table, groupby_fields, use_case, ml_approach, domain_metadata)
        
        # print("system prompt",system_prompt,"user prompt",user_prompt)
            # Call LLM for join suggestions
        response, cost = self.call_llm( system_prompt, user_prompt)     
        # Get LLM response
        # print(f"llm response {response}")
        

        # Parse LLM response
        parsed_output = self._parse_llm_output(response)
        # print(f"parsed output {parsed_output}")

        
        return parsed_output, cost
    
   
    def call_llm(self, system_prompt, user_prompt):
        try:
            response, cost = self.ai_handler.route_to(
                    llm_provider=self.config.ai_provider,
                    configuration={
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": self.config.temperature,
                        "max_tokens": self.config.max_tokens,
                    },
                    model= self.config.model_name
                )
            
            return response, cost
        
        except Exception as e:
            self.logger.error(f"Error in LLM output response: {str(e)}")
            raise e

    
    
    def _parse_llm_output(self, llm_response):
        # Parse LLM response
        # Cleans an LLM JSON-like string output.
        # pydantic class validation
        try:
            cleaned = clean_json_string(llm_response)
            parsed_output = JoinOutput.model_validate_json(cleaned)
            self.logger.info(f"Successfully parsed and validated LLM response for {self.operation}!!!")
            return parsed_output
        except ValidationError as e:
            self.logger.error(f"Parsing failed with validation error: {e}")
            raise e


    



        
    

