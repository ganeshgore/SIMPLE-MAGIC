@echo off
DOSKEY smagic = docker run -it --rm -v  %cd%:/simple-magic goreganesh/simple-magic $*
DOSKEY smagiccv = docker run -it --rm -v  %cd%:/simple-magic-cv goreganesh/simple-magic-cv $*
