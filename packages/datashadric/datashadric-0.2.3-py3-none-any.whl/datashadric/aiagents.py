# -*- coding: utf-8 -*-
"""
AI Agents Functions and Classes Module
Comprehensive collection of AI agent utilities for data analysis, natural language processing, and more.
"""

# OS and environment imports
import os

# Typing and formatting imports
from typing import Any, Dict, Optional
import re, base64, ast

# Standard libraries for web requests and JSON handling
import requests, json

# Large Language Model and Multimodal APIs
import openai, anthropic
import google.generativeai as genai
from PIL import Image

# Some imports from datashadric package
from datashadric.dataframing import dsdf
from datashadric.plotters import dsplt


def ai_generate_text(prompt: str, model: str = "gemini-2.5-flash", max_tokens: int = 150) -> str:
    """Generate text using Google's GEMINI models (without embeddings)"""
    genai.api_key = os.getenv("GEMINI_API_KEY")
    response = genai.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens
    )
    return response.choices[0].text.strip()


def ai_generate_image(prompt: str, model: str = "gemini-2.5-flash-image-preview", size: str = "1024x1024") -> Image.Image:
    """Generate an image using Google's GEMINI models - Nano Banana"""
    genai.api_key = os.getenv("GEMINI_API_KEY")
    response = genai.Image.create(
        prompt=prompt,
        n=1,
        size=size,
        model=model
    )
    image_url = response['data'][0]['url']
    image = Image.open(requests.get(image_url, stream=True).raw)
    return image


def ai_visual_recognition(image_path: str, model: str = "gemini-2.5-flash") -> str:
    """Perform visual recognition using Google's GEMINI Vision models"""
    genai.api_key = os.getenv("GEMINI_API_KEY")
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    response = genai.Vision.recognize(
        model=model,
        image=image_data
    )
    return response['description']


def ai_analyze_plot_data_with_vision(df: Any = None, excel_path=None, image_path=None, col_x=None, col_y=None, prompt: str = "") -> str:
    """Analyze data using AI with a generated plot"""
    # Analyze plot with AI Vision
    ai_provider = "gemini"
    genai.api_key = os.getenv("GEMINI_API_KEY")
    if df is None:
        df = dsdf.df_load_dataset(excel_path)
    else:
        df = df
    if image_path is None:
        image = dsplt.df_scatter_plotter(df, col_x, col_y, save_path="temp_plot.png")
        image_path = "temp_plot.png"
    else:
        image_path = image_path
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    if prompt == "":
        prompt = (
            "You are an expert Data Scientist, and you are given a task to Identify and describe any outlier or anomalous points in this plot, we want to have well-defined data, that fits trends that are easy to visualise inorder to aid in gaining insights from the experiment. "
            "The outliers are often as follows: "
            "1) points that deviate significantly from the overall trend or pattern in the data, and/or "
            "2) points that lie on a purely vertical trend line usually at the end of the plot (towards the right of the image), and/or "
            "3) sometimes, the outliers are small (tight) point clouds that occur some distance from the rest of the scatter trend. "
            "In addition, assess other types of outliers in analytical fashion as per your knowledge as a data scientist."
            "Wherever possible, estimate their coordinates or describe their location, such that it is easy to either 1) create anomalous point clouds in the form of boundary boxes for the points that are anomalous, so as to remove them in bulk and/or 2) identify each point by it's coordinates and thus make it removable from the dataset. "
            "In your output, be concise and only focus on the anomalies. In fact give me the bounding boxes in the Example format: boxes = [(x1, y1, x2, y2), ...] separated by a line skip before you start giving that portion of output, this will allows me to directly look for it and get data from it"
        )
    else:
        prompt = prompt
    response = genai.Vision.analyze(
        model="gemini-2.5-flash",
        image=image_data,
        prompt=prompt
    )
    if df is None:
        df = dsdf.df_load_dataset(excel_path)
    print(df.head())
    print(f"Analyzing plot image using {ai_provider.upper()}...")
    description = response.text
    print("AI analysis:\n", description)
    boxes = None
    match = re.search(r'boxes\s*=\s*\[(.*?)\]', description, re.DOTALL)
    if match:
        boxes_str = match.group(1)
        try:
            boxes = ast.literal_eval(f'[{boxes_str}]')
            print(f"\n✓ Extracted boxes from AI output: {boxes}")
        except Exception as e:
            print(f"\n✗ Failed to parse boxes: {e}")
            boxes = [(100, 150, 120, 170)]
    else:
        print("\n✗ No boxes found in AI output, using default")
        boxes = [(100, 150, 120, 170)]
    if boxes:
        points_removed = 0
        print(f"  Original dataset: {len(df)} rows")
        for box in boxes:
            x_min, y_min, x_max, y_max = box
            print(f"x_min: {x_min}")
            print(f"x_max: {x_max}")
            print(f"y_min: {y_min}")
            print(f"y_max: {y_max}")
            print(f"\nRemoving points where X is between {x_min} and {x_max}, and Y is between {y_min} and {y_max}")
            mask = (df[col_x] >= x_min) & (df[col_x] <= x_max) & (df[col_y] >= y_min) & (df[col_y] <= y_max)
            points_removed += mask.sum()
            df = df[~mask]
        # Pass all boxes at once for annotation
        new_plot = dsplt.df_scatterplot_boundingboxes_plotter(df, col_x, col_y, boxes, title="Plot with Bounding Boxes", save_path="temp_plot_with_boxes.png")
        # df.to_excel("cleaned_dataset.xlsx", index=False)
        # print(f"✓ Cleaned dataset saved as cleaned_dataset.xlsx")
        print(f"\033[91m    Found {points_removed} anomalous points to remove\033[0m")
        print(f"\033[91m    Cleaned dataset: {len(df)} rows ({points_removed} rows removed)\033[0m")
    else:
        print("No valid boxes to process")
    print("_" * 75)
    return df

def ai_analyze_plot_data_with_bounding_boxes(df: Any = None, excel_path=None, image_path=None, col_x=None, col_y=None, prompt: str = "") -> str:
    """Analyze data using AI with a generated plot and return bounding boxes of anomalies"""    
    # Analyze plot with AI
    ai_provider = "gemini"
    genai.api_key = os.getenv("GEMINI_API_KEY")
    if df is None:
        df = dsdf.df_load_dataset(excel_path)
    else:
        df = df
    if image_path is None:
        image = dsplt.df_scatter_plotter(df, col_x, col_y, save_path="temp_plot.png")
        image_path = "temp_plot.png"
    else:
        image_path = image_path
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        if prompt == "":
            prompt = (
                "You are an expert Data Scientist, and you are given a task to Identify and describe any outlier or anomalous points in this plot, we want to have well-defined data, that fits trends that are easy to visualise inorder to aid in gaining insights from the experiment. "
                "The outliers are often as follows: "
                "1) points that deviate significantly from the overall trend or pattern in the data, and/or "
                "2) points that lie on a purely vertical trend line usually at the end of the plot (towards the right of the image), and/or "
                "3) sometimes, the outliers are small (tight) point clouds that occur some distance from the rest of the scatter trend. "
                "In addition, assess other types of outliers in analytical fashion as per your knowledge as a data scientist."
                "Wherever possible, estimate their coordinates or describe their location, such that it is easy to either 1) create anomalous point clouds in the form of boundary boxes for the points that are anomalous, so as to remove them in bulk and/or 2) identify each point by it's coordinates and thus make it removable from the dataset. "
                "In your output, be concise and only focus on the anomalies. In fact give me the bounding boxes in the Example format: boxes = [(x1, y1, x2, y2), ...] separated by a line skip before you start giving that portion of output, this will allows me to directly look for it and get data from it"
            )
        else:
            prompt = prompt
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([image_data, prompt])
        if df is None:
            df = dsdf.df_load_dataset(excel_path)
        print(df.head())
        print(f"Analyzing plot image using {ai_provider.upper()}...")
        description = response.text
        print("AI analysis:\n", description)
        boxes = None
        match = re.search(r'boxes\s*=\s*\[(.*?)\]', description, re.DOTALL)
        if match:
            boxes_str = match.group(1)
            try:
                boxes = ast.literal_eval(f'[{boxes_str}]')
                print(f"\n✓ Extracted boxes from AI output: {boxes}")
            except Exception as e:
                print(f"\n✗ Failed to parse boxes: {e}")
                boxes = [(100, 150, 120, 170)]
        else:
            print("\n✗ No boxes found in AI output, using default")
            boxes = [(100, 150, 120, 170)]
        if boxes:
            points_removed = 0
            print(f"  Original dataset: {len(df)} rows")
            for box in boxes:
                x_min, y_min, x_max, y_max = box
                print(f"x_min: {x_min}")
                print(f"x_max: {x_max}")
                print(f"y_min: {y_min}")
                print(f"y_max: {y_max}")
                print(f"\nRemoving points where X is between {x_min} and {x_max}, and Y is between {y_min} and {y_max}")
                mask = (df[col_x] >= x_min) & (df[col_x] <= x_max) & (df[col_y] >= y_min) & (df[col_y] <= y_max)
                points_removed += mask.sum()
                df = df[~mask]
            # Pass all boxes at once for annotation
            new_plot = dsplt.df_scatterplot_boundingboxes_plotter(df, col_x, col_y, boxes, title="Plot with Bounding Boxes", save_path="temp_plot_with_boxes.png")
            # df.to_excel("cleaned_dataset.xlsx", index=False)
            # print(f"✓ Cleaned dataset saved as cleaned_dataset.xlsx")
            print(f"\033[91m    Found {points_removed} anomalous points to remove\033[0m")
            print(f"\033[91m    Cleaned dataset: {len(df)} rows ({points_removed} rows removed)\033[0m")
        else:
            print("No valid boxes to process")
        print("_" * 75)
        return df


    def ai_data_insights_summary(df: Any, prompt: str = None) -> str:
        """Generate data insights summary using AI"""
        ai_provider = "gemini"
        genai.api_key = os.getenv("GEMINI_API_KEY")
        data_summary = df.describe().to_string()
        if prompt is None:
            prompt = "Provide a concise summary of key insights from the data summary, focus on the deep insights and metrics that describe the data, the relationships between features and which features predict each other. Also, give us which features are redundant and which are not contributing to the model as well as those that high high direct contribution to outcomes. You can make each section easy to read and produce a .md of the insights for the data but also output the insights to the shell for the analyst to quickly visualise."
        else:
            prompt = prompt
        full_prompt = f"Given the following data summary:\n{data_summary}\n\n{prompt}"
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([full_prompt])
        insights = response.text
        return insights