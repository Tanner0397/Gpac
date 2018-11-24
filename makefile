all: builder

builder:
	CFLAGS="-O2 -std=c++11" python3 src/setup.py build_ext --build-lib build

clean:
	rm -r build/*
