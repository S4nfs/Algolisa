![DLI Header](images/nvidia_header.png)

# Welcome to the MONAI Label DLI

MONAI Label minimizes the need for developers and researchers to manually annotate data by providing an intelligent imaging labeling and learning SDK that can be integrated into either customized or template-based data labeling apps. MONAI Label saves developers time, helping them quickly progress to training, tuning, and validating their medical AI models within the MONAI standardized paradigm.

The industry’s most popular open source viewers already have MONAI integrated: 3D Slicer, OHIF, QuPath, Digital Slide Archive, and CVAT, and it is also integrated into cloud service providers. Developers can also incorporate MONAI Label into their custom viewer using server and client APIs, which are well abstracted and documented for seamless integration.

In this lab, you'll learn more about the MONAI Label and then get a chance to explore different use cases and viewer.  This DLI is based on the MONAI Toolkit Container Docker Image which means that you'll have also access to the MONAI Toolkit.

## Table of Contents
- What is MONAI?
- Lab Content
- MONAI Toolkit

## What is MONAI?

NVIDIA co-founded Project MONAI, the Medical Open Network for AI, with the world’s leading academic medical centers to establish an inclusive community of AI researchers to develop and exchange best practices for AI in healthcare imaging across academia and enterprise researchers.

MONAI is the domain-specific, open-source Medical AI framework that drives research breakthroughs and accelerates AI into clinical impact. MONAI unlocks the power of medical data to build deep learning models for medical AI workflows. MONAI provides the essential domain-specific tools from data labeling to model training, making it easy to develop, reproduce and standardize medical AI lifecycles

<a href="https://monai.io" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">MONAI Website</a>

## Lab Content
In this lab, aims to introduce you to the MONAI Label and and its applications in medical image analysis. You'll start with an example of a basic workflow using 3D Slicer and MONAI Label.

The lab provides different workflows, which are specific to different medical imaging modalities, such as radiology, pathology, and endoscopy/video workflows. The lab will cover the different viewers that are relevant to each workflow, such as OHIF, XNAT, QuPath, impartial, and CVAT.

During the lab, you'll launch a MONAI Label server, load data, and run an annotation/inference/training workflow. By the end of the lab, you should be able to create segmentation masks and run inference/training for medical images using an AI-Assisted workflow.

<a href="01_3dslicer.ipynb" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">Lab 1: 3D Slicer</a>
<a href="02_myapp.ipynb" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">Lab 2: My Sample App</a>
<a href="03_ohif.ipynb" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">Lab 3: (Radiology) OHIF</a>
<a href="04_xnat.ipynb" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">Lab 4: (Radiology) XNAT</a>
<a href="05_xnat_deploy.ipynb" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">Lab 5: (Radiology) Deployment workflow using XNAT </a>
<a href="06_3dslicer_vista3dnim.ipynb" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">Lab 6: VISTA-3D NIM with 3D Slicer </a>
<a href="12_impartial4pathology.ipynb" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">Lab 7: (Pathology) ImPartial</a>
<a href="11_Qupath4pathology.ipynb" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">Lab 8: (Pathology) QuPath</a>
<a href="13_Cvat4Vedios.ipynb" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">Lab 9: (Endo/Video) CVAT</a>


## MONAI Toolkit Content
MONAI Toolkit is a development sandbox offered as part of MONAI Enterprise, an NVIDIA AI Enterprise-supported distribution of MONAI. This container is based on the MONAI Toolkit container and you can find all of the Toolkit Content in the `toolkit` directory located in the parent directory within Jupyter Lab. 

<a href="../toolkit/0-welcome.md" target="_blank" style="display: inline-block; border: 1px solid gray; border-radius: 10px; padding: 5px 10px 5px 10px; background-color: white; margin: 5px 20px 5px 0px; ">MONAI Toolkit Directory</a>


To setup the MONAI Toolkit on your own machine, you can find instructions and the container image located on [NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/clara/containers/monai-toolkit).

For more information on enterprise support visit the [NVIDIA AI Enterprise page](https://www.nvidia.com/en-us/data-center/products/ai-enterprise/).

