/******************************************************************************
* $HeadURL: https://svnpub.iter.org/codac/iter/codac/dev/units/m-cpp-common/tags/CODAC-CORE-6.2B2/src/main/c++/tools/CyclicRedundancyCheck.h $
* $Id: CyclicRedundancyCheck.h 100814 2019-07-17 13:23:31Z bauvirb $
*
* Project       : CODAC Core System
*
* Description   : CyclicRedundancyCheck computation
*
* Author        : Bertrand Bauvir (IO)
*
* Copyright (c) : 2010-2019 ITER Organization,
*                 CS 90 046
*                 13067 St. Paul-lez-Durance Cedex
*                 France
*
* This file is part of ITER CODAC software.
* For the terms and conditions of redistribution or use of this software
* refer to the file ITER-LICENSE.TXT located in the top level directory
* of the distribution package.
******************************************************************************/

#ifndef _CyclicRedundancyCheck_h
#define _CyclicRedundancyCheck_h

/**
 * @file CyclicRedundancyCheck.h
 * @brief Header file for CRC computation
 * @date 18/04/2017
 * @author Bertrand Bauvir (IO)
 * @copyright 2010-2017 ITER Organization
 * @detail This header file contains the definition of the CyclicRedundancyCheck<> methods.
 */

// Global header files
// Local header files

#include <stdio.h>
#include <stdlib.h>
// Constants

// Type definition



// Global variables




// Function declaration

/**
 * @brief CRC operation .. Initialise __table from CRC polynomial
 * @return True.
 */


/**
 * @brief CRC operation
 * @detail This method implements a cyclic redundancy check on a sized byte array with an optional
 * seed in case the same binary buffer needs to produce different checksum for distinct uses.
 * @return The CRC over the sized array.
 */


// Function definition


extern "C" {


unsigned int CyclicRedundancyCheck (const unsigned int poly, const unsigned char * const buffer, const unsigned int size, const unsigned int seed)
{
  
  bool __table_init = false;
  unsigned int __table [256];

  bool status = (__table_init == false);

  if (status)
    {
      for (unsigned int __table_index = 0u; __table_index < 256u; __table_index++) 
        {
          unsigned int seed  = __table_index;
          
          for (unsigned int bit_index = 0u; bit_index < 8u; bit_index++) 
            {
              if (0x01u == (seed & 0x01u))
                {
                  seed = poly ^ (seed >> 1);
                }
              else 
                {
                  seed = seed >> 1;
                }
            }
          
          __table[__table_index] = seed;
        }
      
      __table_init = true;
      status = true;
    }


  unsigned int chksum = 0xFFFFFFFFul; // Initial value

  if (0u != seed)
    {
      chksum = __table[(chksum ^ reinterpret_cast<const unsigned char*>(&seed)[0]) & 0xFFu] ^ (chksum >> 8);
      chksum = __table[(chksum ^ reinterpret_cast<const unsigned char*>(&seed)[1]) & 0xFFu] ^ (chksum >> 8);
      chksum = __table[(chksum ^ reinterpret_cast<const unsigned char*>(&seed)[2]) & 0xFFu] ^ (chksum >> 8);
      chksum = __table[(chksum ^ reinterpret_cast<const unsigned char*>(&seed)[3]) & 0xFFu] ^ (chksum >> 8);
    }


  for (unsigned int index = 0u; index < size; index++){
      chksum = __table[(chksum ^ buffer[index]) & 0xFFu] ^ (chksum >> 8);
}

  printf("PRECHECK: %u\n", chksum);

  chksum = chksum ^ 0xFFFFFFFFul;

  printf("POSTCHECK: %u\n", chksum);

  unsigned int finalCheck = chksum;  
   
  return finalCheck;

}

}

#endif // _CyclicRedundancyCheck_h

