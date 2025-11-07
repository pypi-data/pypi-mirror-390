#!/usr/bin/env bash

# This script is not supposed to run alone
# Must be used with the Makefile of this export

OBJDIR=build
BINDIR=bin

cmake -B$OBJDIR $@
cmake --build $OBJDIR

# Add write permissions for users 
# to clean build and bin folders outside the container
if [ -d "$OBJDIR" ]; then
    chmod -R a+w $OBJDIR
fi
if [ -d "$BINDIR" ]; then
    chmod -R a+w $BINDIR
fi
