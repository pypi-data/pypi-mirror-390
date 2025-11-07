/*
    (C) Copyright 2017 CEA LIST. All Rights Reserved.
    Contributor(s): N2D2 Team

    This software is governed by the CeCILL-C license under French law and
    abiding by the rules of distribution of free software.  You can  use,
    modify and/ or redistribute the software under the terms of the CeCILL-C
    license as circulated by CEA, CNRS and INRIA at the following URL
    "http://www.cecill.info".

    As a counterpart to the access to the source code and  rights to copy,
    modify and redistribute granted by the license, users are provided only
    with a limited warranty  and the software's author,  the holder of the
    economic rights,  and the successive licensors  have only  limited
    liability.

    The fact that you are presently reading this means that you have had
    knowledge of the CeCILL-C license and that you accept its terms.
*/

#ifndef __ASSERT_H__
#define __ASSERT_H__

#ifdef __cplusplus
extern "C" {
#endif 

#include <stdio.h>

inline void assert_failure(const char* msg, const char* file, int line) 
{
    printf("Assert failure: %s in %s:%d.\r\n", msg, file, line);
    while(1) {}
}

#ifdef NDEBUG
#define assert(test) ((void)0)
#define assertm(test, msg) ((void)0)
#else
#define assert(test) do { if(!(test)) { assert_failure("error", __FILE__, __LINE__); } } while(0)
#define assertm(test, msg) do { if(!(test)) { assert_failure(msg, __FILE__, __LINE__); } } while(0)
#endif 

#ifdef __cplusplus
}
#endif 

#endif
