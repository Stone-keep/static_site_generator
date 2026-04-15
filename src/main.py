import logging

logging.basicConfig(
    filename='ssg.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

from functions import copy_files, generate_pages_recursive


def main():
   
   copy_files("static", "public")
   generate_pages_recursive("content", "template.html", "public")

if __name__ == "__main__":
    main()