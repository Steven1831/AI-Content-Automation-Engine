icg-s-step1:
	poetry run python -m flows.image_content_generator.pipeline.main short step1

icg-s-step2:
	poetry run python -m flows.image_content_generator.pipeline.main short step2

icg-s-step3:
	poetry run python -m flows.image_content_generator.pipeline.main short step3

icg-s-step4:
	poetry run python -m flows.image_content_generator.pipeline.main short step4

icg-s-step5:
	poetry run python -m flows.image_content_generator.pipeline.main short step5

icg-s-step6:
	poetry run python -m flows.image_content_generator.pipeline.main short step6

icg-s-step7:
	poetry run python -m flows.image_content_generator.pipeline.main short step7

icg-s-all:
	poetry run python -m flows.image_content_generator.pipeline.main short all
