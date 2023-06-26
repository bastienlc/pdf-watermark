from inputs import UserInputs
from utils import add_watermark_to_pdf

add_watermark_to_pdf(UserInputs("test.pdf", save_to="result.pdf"))
