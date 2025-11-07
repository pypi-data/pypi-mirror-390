#####################################################################
##: Different options to compile the export
##: Usage :
##:
##:    make / make help
##:         display the different options available
##:    make build
##:         compile the export on host for C/C++ apps
##:         (generate an executable in build/bin)
##:    make build_image_docker
##:         generate the docker image of the arm compiler
##:    make build_docker
##:         compile the export in a container for C/C++ apps
##:         (generate an executable in build/bin)
##:    make clean
##:         clean up the build and bin folders
##:
#####################################################################



MAKEFLAGS := --no-print-directory
DOCKER_COMPILER := tools/arm-none-eabi_compiler.Dockerfile
IMAGE := arm:arm-none-eabi_compiler
BOARD := stm32f7

OBJDIR := build
BINDIR := bin
TARGET := ${BINDIR}/aidge_STM32F7.elf
FLASH_LD := STM32F746ZGTx_FLASH.ld
HAL_HEADER_FILE := stm32f7xx_hal.h

MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(dir $(MAKEFILE_PATH))

COMMON_FLAGS := -DHAL_HEADER="<${HAL_HEADER_FILE}>" -DNDEBUG -Ofast -Wall -Wno-unused-variable -specs=nano.specs -c -mcpu=cortex-m7 -mfloat-abi=hard -mfpu=fpv5-d16 -DUSE_HAL_DRIVER -DSTM32F746xx -DARM_MATH_CM7 -MMD
INCLUDE_DIRS := -I. -I./Inc -I./dnn -I./dnn/include -I./Drivers/STM32F7xx_HAL_Driver/Inc -I./Drivers/STM32F7xx_HAL_Driver/Inc/Legacy -I./Drivers/CMSIS/Device/ST/STM32F7xx/Include -I./Drivers/CMSIS/Include
LINK_FLAGS := $(LINK_FLAGS) -mcpu=cortex-m7 -mfloat-abi=hard -mfpu=fpv5-d16 -T${FLASH_LD} -lc -lm -lnosys -specs=nano.specs -flto -Wl,--print-memory-usage -u _printf_float

PREFIX := arm-none-eabi
CC := $(PREFIX)-gcc
CC_FLAGS := ${COMMON_FLAGS} -std=gnu11
CC_SRCS := $(shell find -name '*.c')
CC_OBJS := $(patsubst %.c,$(OBJDIR)/%.c.o,$(CC_SRCS))
DEPENDENCIES := $(patsubst %.c.o,%.c.d,$(CC_OBJS))

CXX := $(PREFIX)-g++
CXX_FLAGS := ${COMMON_FLAGS} -std=c++14 -fno-exceptions -fno-rtti
CXX_SRCS := $(shell find -name '*.cpp')
CXX_OBJS := $(patsubst %.cpp,$(OBJDIR)/%.cpp.o,$(CXX_SRCS))
DEPENDENCIES := $(DEPENDENCIES) $(patsubst %.cpp.o,%.cpp.d,$(CXX_OBJS))

ASM := $(PREFIX)-gcc
ASM_FLAGS := ${COMMON_FLAGS} -x assembler-with-cpp
ASM_SRCS := $(shell find -name '*.s')
ASM_OBJS := $(patsubst %.s,$(OBJDIR)/%.s.o,$(ASM_SRCS))



all: help

build: ${CC_OBJS} ${CXX_OBJS} ${ASM_OBJS}
	@mkdir -p $(dir ${TARGET})
	@chmod -R 777 $(OBJDIR)
	${CC} ${CC_OBJS} ${CXX_OBJS} ${ASM_OBJS} ${LINK_FLAGS} -o ${TARGET}
	@chmod -R 777 $(BINDIR)

${OBJDIR}/%.c.o: %.c
	@mkdir -p $(dir $@)
	@chmod -R 777 $(OBJDIR)
	${CC} ${CC_FLAGS} ${INCLUDE_DIRS} -o $@ $<
	@chmod -R 777 $(OBJDIR)

${OBJDIR}/%.cpp.o: %.cpp
	@mkdir -p $(dir $@)
	@chmod -R 777 $(OBJDIR)
	${CXX} ${CXX_FLAGS} ${INCLUDE_DIRS} -o $@ $<
	@chmod -R 777 $(OBJDIR)

${OBJDIR}/%.s.o: %.s
	@mkdir -p $(dir $@)
	@chmod -R 777 $(OBJDIR)
	${ASM} ${ASM_FLAGS} -o $@ $<
	@chmod -R 777 $(OBJDIR)


.PHONY: clean help

clean:
	if [ -d "${OBJDIR}" ]; then rm -rf ${OBJDIR}; fi
	if [ -d "${BINDIR}" ]; then rm -rf ${BINDIR}; fi
	rm -f ZAsm/assembly_file.s

asm:
	${CXX} -S ZAsm/assembly_file.cpp
	mv assembly_file.s ZAsm/

help:
	@grep -e "^##:"  Makefile;

# Makefile target for building the arm-none-eabi compiler image
.PHONY: build_image_docker

build_image_docker:
	@docker build --pull --rm -f "${DOCKER_COMPILER}" -t ${IMAGE} tools/

# Makefile targets for building export app via docker
.PHONY: build_docker

build_export_docker:
	@docker run --rm --name ${BOARD}_compiling -v "${MAKEFILE_DIR}":/usr/src/export -w /usr/src/export ${IMAGE} make build

clean_export_docker:
	@docker run --rm --name ${BOARD}_compiling -v "${MAKEFILE_DIR}":/usr/src/export -w /usr/src/export ${IMAGE} make clean

-include $(DEPENDENCIES)

