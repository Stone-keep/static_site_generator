import logging

logging.basicConfig(
    filename='ssg.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

import sys
from functions import copy_files, generate_pages_recursive

basepath = "/"
if len(sys.argv) > 1:
    basepath = sys.argv[1]


def main():
   
   copy_files("static", "docs")
   generate_pages_recursive("content", "template.html", "docs", basepath)
   


if __name__ == "__main__":
    main()