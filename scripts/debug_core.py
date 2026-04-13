import time
start = time.time()
print("1. Importing Flask components...")
from flask import Flask, request, jsonify, render_template
print(f"Done in {time.time() - start:.2f}s")

start = time.time()
print("2. Importing CORS...")
from flask_cors import CORS
print(f"Done in {time.time() - start:.2f}s")

start = time.time()
print("3. Importing other core modules...")
import asyncio, json, os, threading, queue, argparse
from datetime import datetime
print(f"Done in {time.time() - start:.2f}s")
print("All core imports success!")
