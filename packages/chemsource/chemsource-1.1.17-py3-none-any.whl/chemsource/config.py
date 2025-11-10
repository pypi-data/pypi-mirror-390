"""
Configuration module for chemsource.

This module contains configuration classes and constants used throughout the chemsource package.
"""

from typing import Optional, List, Any

#: Default prompt template for chemical compound classification
BASE_PROMPT = ("You are a helpful scientist that will classify the provided compound \
COMPOUND_NAME using only the information provided as any combination of the \
following: MEDICAL, ENDOGENOUS, FOOD, PERSONAL CARE, INDUSTRIAL. Note that \
MEDICAL refers to compounds actively used as approved medications in \
humans or in late-stage clinical trials in humans. Note that ENDOGENOUS \
refers to compounds that are produced by the human body specifically. \
ENDOGENOUS excludes essential nutrients that cannot be synthesized by the \
human body. Note that FOOD refers to compounds present in natural food items \
or food additives. Note that PERSONAL CARE refers to non-medicated compounds \
typically used for activities such as skincare, beauty, and fitness. Note \
that INDUSTRIAL should be used only for synthetic compounds not used as a \
contributing ingredient in the medical, personal care, or food industries. \
Specify INFO instead if more information is needed. DO NOT MAKE ANY \
ASSUMPTIONS, USE ONLY THE INFORMATION PROVIDED AFTER THE COMPOUND NAME \
BY THE USER. A classification of INFO will also be rewarded when \
correctly applied and is strongly encouraged if information is of poor \
quality, if there is not enough information, or if you are not completely \
confident in your answer.  Provide the output as a plain text separated \
by commas, and provide only the categories listed (either list a \
combination of INDUSTRIAL, ENDOGENOUS, PERSONAL CARE, MEDICAL, FOOD or \
list INFO), with no justification. Provided Information:\n")


class Config:
    """
    Configuration class for chemsource parameters.
    
    This class manages all configuration parameters for the chemsource system,
    including API keys, model settings, and output formatting options.
    
    Args:
        model_api_key (str, optional): API key for the language model service.
        model (str, optional): Name of the language model to use. Defaults to "gpt-4o".
        temperature (float, optional): Temperature parameter for model creativity. Defaults to 0.
        top_p (float, optional): Top-p parameter for nucleus sampling. Defaults to 0.
        ncbi_key (str, optional): API key for NCBI/PubMed access.
        prompt (str, optional): Custom prompt template. Defaults to BASE_PROMPT.
        max_tokens (int, optional): Maximum number of tokens for model context. Defaults to 250000.
        clean_output (bool, optional): Whether to clean and validate output. Defaults to False.
        explanation (bool, optional): Whether to expect explanations in model responses. 
                                     Only effective when clean_output=True. Defaults to False.
        explanation_separator (str, optional): Delimiter separating explanation from classification.
                                              Only used when both clean_output and explanation are True.
                                              Defaults to "EXPLANATION_COMPLETE".
        allowed_categories (List[str], optional): List of allowed categories for filtering. Defaults to None.
        custom_client (Any, optional): Custom OpenAI client instance. Defaults to None.
    
    Attributes:
        model_api_key (str): The model API key.
        model (str): The language model name.
        temperature (float): The temperature parameter.
        top_p (float): The top-p parameter.
        ncbi_key (str): The NCBI API key.
        prompt (str): The prompt template.
        max_tokens (int): The maximum token limit.
        clean_output (bool): Whether output cleaning is enabled.
        explanation (bool): Whether to extract explanations from responses.
        explanation_separator (str): The delimiter for separating explanations.
        allowed_categories (List[str]): The allowed categories list.
        custom_client (Any): The custom client instance.
    """
    
    def __init__(self, 
                 model_api_key: Optional[str] = None, 
                 model: str = "gpt-4o", 
                 temperature: float = 0, 
                 top_p: float = 0.0000001, 
                 ncbi_key: Optional[str] = None,
                 prompt: str = BASE_PROMPT, 
                 max_tokens: int = 250000, 
                 clean_output: bool = False, 
                 explanation: bool = False,
                 explanation_separator: str = "EXPLANATION_COMPLETE",
                 output_explanation: bool = False,
                 allowed_categories: Optional[List[str]] = None, 
                 custom_client: Optional[Any] = None) -> None:
        self.model_api_key = model_api_key
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.ncbi_key = ncbi_key
        self.prompt = prompt
        self.max_tokens = max_tokens
        self.clean_output = clean_output
        self.explanation = explanation
        self.explanation_separator = explanation_separator
        self.output_explanation = output_explanation
        self.allowed_categories = allowed_categories
        self.custom_client = custom_client
    
    def set_ncbi_key(self, ncbi_key: Optional[str]) -> None:
        """
        Set the NCBI API key.
        
        Args:
            ncbi_key (str, optional): The NCBI API key to set.
        """
        self.ncbi_key = ncbi_key

    def set_model_api_key(self, model_api_key: Optional[str]) -> None:
        """
        Set the model API key.
        
        Args:
            model_api_key (str, optional): The model API key to set.
        """
        self.model_api_key = model_api_key

    def set_model(self, model: str) -> None:
        """
        Set the language model name.
        
        Args:
            model (str): The name of the language model to use.
        """
        self.model = model

    def set_prompt(self, prompt: str) -> None:
        """
        Set the prompt template.
        
        Args:
            prompt (str): The prompt template to use for classification.
        """
        self.prompt = prompt

    def set_token_limit(self, max_tokens: int) -> None:
        """
        Set the maximum token limit.
        
        Args:
            max_tokens (int): The maximum number of tokens for model context.
        """
        self.max_tokens = max_tokens

    def set_temperature(self, temperature: float) -> None:
        """
        Set the temperature parameter for model creativity.
        
        Args:
            temperature (float): The temperature value (0.0 to 1.0).
        """
        self.temperature = temperature

    def set_top_p(self, top_p: float) -> None:
        """
        Set the top-p parameter for nucleus sampling.
        
        Args:
            top_p (float): The top-p value (0.0 to 1.0).
        """
        self.top_p = top_p

    def set_clean_output(self, clean_output: bool) -> None:
        """
        Set whether to enable output cleaning and validation.
        
        Args:
            clean_output (bool): Whether to clean and validate output.
        """
        self.clean_output = clean_output
    
    def set_explanation(self, explanation: bool) -> None:
        """
        Set whether to include explanations in the output.
        
        Args:
            explanation (bool): Whether to include explanations.
        """
        self.explanation = explanation
    
    def set_explanation_separator(self, explanation_separator: str) -> None:
        """
        Set the explanation separator string.
        
        Args:
            explanation_separator (str): The string that separates explanations in the output.
        """
        self.explanation_separator = explanation_separator
    
    def set_explanation_output(self, output_explanation: bool) -> None:
        """
        Set whether to output explanations along with classifications.
        
        Args:
            output_explanation (bool): Whether to output explanations.
        """
        self.output_explanation = output_explanation

    def set_allowed_categories(self, allowed_categories: Optional[List[str]]) -> None:
        """
        Set the list of allowed categories for filtering.
        
        Args:
            allowed_categories (List[str], optional): List of allowed categories.
        """
        self.allowed_categories = allowed_categories

    def set_custom_client(self, custom_client: Optional[Any]) -> None:
        """
        Set a custom OpenAI client instance.
        
        Args:
            custom_client (Any, optional): Custom OpenAI client instance.
        """
        self.custom_client = custom_client
    
    def configure(self, 
                  ncbi_key: Optional[str] = None, 
                  model_api_key: Optional[str] = None, 
                  model: str = "gpt-4o", 
                  temperature: float = 0, 
                  top_p: float = 0,
                  prompt: str = BASE_PROMPT, 
                  max_tokens: int = 250000, 
                  clean_output: bool = False, 
                  explanation: bool = False,
                  explanation_separator: str = "EXPLANATION_COMPLETE",
                  output_explanation: bool = False,
                  allowed_categories: Optional[List[str]] = None, 
                  custom_client: Optional[Any] = None) -> None:
        """
        Configure all parameters at once.
        
        Args:
            ncbi_key (str, optional): API key for NCBI/PubMed access.
            model_api_key (str, optional): API key for the language model service.
            model (str, optional): Name of the language model to use. Defaults to "gpt-4o".
            temperature (float, optional): Temperature parameter for model creativity. Defaults to 0.
            top_p (float, optional): Top-p parameter for nucleus sampling. Defaults to 0.
            prompt (str, optional): Custom prompt template. Defaults to BASE_PROMPT.
            max_tokens (int, optional): Maximum number of tokens for model context. Defaults to 250000.
            clean_output (bool, optional): Whether to clean and validate output. Defaults to False.
            explanation (bool, optional): Whether to expect explanations in model responses. Defaults to False.
            explanation_separator (str, optional): Delimiter separating explanation from classification.
                                                  Defaults to "EXPLANATION_COMPLETE".
            output_explanation (bool, optional): Whether to return the explanation text alongside classification.
                                                Defaults to False.
            allowed_categories (List[str], optional): List of allowed categories for filtering. Defaults to None.
            custom_client (Any, optional): Custom OpenAI client instance. Defaults to None.
        """
        self.model_api_key = model_api_key
        self.model = model
        self.ncbi_key = ncbi_key
        self.prompt = prompt
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.clean_output = clean_output
        self.explanation = explanation
        self.explanation_separator = explanation_separator
        self.output_explanation = output_explanation
        self.allowed_categories = allowed_categories
        self.custom_client = custom_client

    def configuration(self) -> dict:
        """
        Get the current configuration as a dictionary with masked sensitive data.
        
        Returns:
            dict: A dictionary containing all configuration parameters with API keys masked.
        """
        if self.model_api_key is None:
            model_api_key_display = None
        else:
           model_api_key_display = "*" * len(self.model_api_key)

        if self.ncbi_key is None:
            ncbi_key_display = None
        else:
            ncbi_key_display =  "*" * len(self.ncbi_key)
        
        return {"model_api_key": model_api_key_display,
                "ncbi_key": ncbi_key_display, 
                "model": self.model,
                "prompt": self.prompt,
                "token_limit": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "clean_output": self.clean_output,
                "explanation": self.explanation,
                "explanation_separator": self.explanation_separator,
                "output_explanation": self.output_explanation,
                "allowed_categories": self.allowed_categories,
                "custom_client": self.custom_client
                }
