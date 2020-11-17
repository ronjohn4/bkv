# bkv
Bag Key Value (bkv) helps develoeprs write applications that need to work with environment values across various environments.
Easy to maintain across Instances
Centralized control
Common API for applications to work with their Bag

Bag - This represents a logical purpose for using a set of keys.  This is generally a single Application but can be shared across applications.
Key - A key is the basic piece of data that can be defined and read.  Some examples are things like: dbPath, copyright, FeatureSwitchA, etc.
Intsance - An instance is where we associate a Bag with an Environment.  Classic Instances are PROD, STAGE, DEV, TEST, TRAIN, etc.
KeyVal - This contains the actual value that will be managed for a given Key, Instance pair.

