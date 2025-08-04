#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

// ANSI Color Codes
#define RED "\x1B[31m"
#define GRN "\x1B[32m"
#define YEL "\x1B[33m"
#define BLU "\x1B[34m"
#define MAG "\x1B[35m"
#define CYN "\x1B[36m"
#define WHT "\x1B[37m"
#define RESET "\x1B[0m"

// Function to get integer input safely
int get_int_input() {
  char input_buffer[32];
  if (fgets(input_buffer, sizeof(input_buffer), stdin) != NULL) {
    return atoi(input_buffer);
  }
  return -1; // Return -1 on EOF or error
}

void print_banner() {
  printf(CYN "****************************************\n" RESET);
  printf(YEL "*                                      *\n" RESET);
  printf(YEL "*      Welcome to the Secret C Store   *\n" RESET);
  printf(YEL "*                                      *\n" RESET);
  printf(CYN "****************************************\n\n" RESET);
  printf("We sell the finest, most elusive secrets.\n");
  printf("Databased Hack&Seek 2025 - Secret C Store\n\n");
}

int main() {
  setbuf(stdout, NULL);
  int account_balance = 1200;

  while (1) {
    system("clear");
    print_banner();
    printf(GRN "Your Account Balance: $%d\n\n" RESET, account_balance);

    if (account_balance < 0) {
      FILE *f = fopen("frenzy.txt", "r");
      if (f == NULL) {
        printf(RED "Server error: frenzy.txt not found. Please contact "
                   "an admin.\n" RESET);
      } else {
        char buf[64];
        if (fgets(buf, sizeof(buf), f)) {
          printf(GRN
                 "\nCongratulations! Your Extra Frenzy Flag order: %s\n" RESET,
                 buf);
        }
        fclose(f);
      }
    }

    printf(BLU "1. Buy Secrets\n" RESET);
    printf(BLU "2. Exit\n" RESET);
    printf("\nEnter your choice: ");

    int menu = get_int_input();

    switch (menu) {
    case 1: {
      printf("\n--- Available Secrets ---\n");
      printf("1. The 'Definitely Not The Flag' Secret (Cost: $1000)\n");
      printf("2. The '1337' Secret (Cost: $100000)\n");
      printf("\nWhich secret would you like to purchase? ");

      int auction_choice = get_int_input();

      if (auction_choice == 1) {
        printf("\nEnter desired quantity: ");
        int number_secrets = get_int_input();

        if (number_secrets > 0) {
          int total_cost = 1000 * number_secrets;
          printf("\nTotal cost for %d secrets: " YEL "$%d\n" RESET,
                 number_secrets, total_cost);

          if (total_cost <= account_balance) {
            account_balance -= total_cost;
            printf(GRN "Purchase successful! Your new balance is $%d\n" RESET,
                   account_balance);
          } else {
            printf(RED "Purchase failed. Insufficient funds.\n" RESET);
          }
        } else {
          printf(RED "Invalid quantity.\n" RESET);
        }
      } else if (auction_choice == 2) {
        printf("\nThis is a high-value secret. We only have one in stock.\n");
        printf("Enter 1 to confirm your purchase for " YEL "$100000" RESET
               ": ");
        int bid = get_int_input();

        if (bid == 1) {
          if (account_balance > 100000) {
            FILE *f = fopen("secret.txt", "r");
            if (f == NULL) {
              printf(RED "Server error: secret.txt not found. Please contact "
                         "an admin.\n" RESET);
            } else {
              char buf[64];
              if (fgets(buf, sizeof(buf), f)) {
                printf(GRN "\nCongratulations! Your order: %s\n" RESET, buf);
                printf("Extra Bonus: Get a free frenzy flag on making your "
                       "bank account negative!\n");
              }
              fclose(f);
            }
            // Exit after flag is revealed
            printf("\nThank you for your business. Terminating connection.\n");
            return 0;
          } else {
            printf(RED "\nTransaction failed. Insufficient funds.\n" RESET);
          }
        }
      } else {
        printf(RED "Invalid selection.\n" RESET);
      }
      break;
    }
    case 2:
      printf("\nThank you for visiting the Secret Store!\n");
      return 0;
    default:
      printf(RED "\nInvalid choice. Please try again.\n" RESET);
      break;
    }
    printf("\nPress Enter to continue...");
    getchar(); // Wait for user to press Enter
  }

  return 0;
}
