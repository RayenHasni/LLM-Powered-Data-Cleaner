class DataCleaning:

    @staticmethod
    def standardize_columns(df):
        """
        Convert column names to lowercase and replace spaces with _
        """
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )
        print("Columns standardized.")
        return df


    @staticmethod
    def remove_duplicates(df):
        """
        Remove duplicate rows
        """
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)

        print(f"Removed {before-after} duplicate rows.")
        return df


    @staticmethod
    def handle_missing(df, strategy="drop"):
        """
        Handle missing values
        
        strategies:
        drop
        mean
        median
        mode
        """
        if strategy == "drop":
            df = df.dropna()

        elif strategy == "mean":
            df = df.fillna(df.mean(numeric_only=True))

        elif strategy == "median":
            df = df.fillna(df.median(numeric_only=True))

        elif strategy == "mode":
            for col in df.columns:
                mode = df[col].mode()
                if not mode.empty:
                    df[col] = df[col].fillna(mode[0])

        print(f"Missing values handled using {strategy}.")
        return df


    @staticmethod
    def convert_types(df, column_types: dict):
        """
        Convert column datatypes
        
        example:
        {"date":"datetime64", "price":"float"}
        """
        try:
            df = df.astype(column_types)
            print("Column types converted.")
        except Exception as e:
            print(f"Type conversion error: {e}")

        return df


    @staticmethod
    def remove_outliers(df, column):
        """
        Remove outliers using IQR method
        """
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        before = len(df)

        df = df[
            (df[column] >= lower) &
            (df[column] <= upper)
        ]

        after = len(df)

        print(f"Removed {before-after} outliers from {column}.")
        return df


    @staticmethod
    def summary(df):
        """
        Display dataset info
        """
        print("Shape:", df.shape)
        print("\nMissing values:")
        print(df.isnull().sum())
        print("\nData types:")
        print(df.dtypes)

        return df.describe()
    
    @staticmethod
    def clean_data(df):
        """All cleaning steps"""
        #df = DataCleaning.standardize_columns(df)
        #df = DataCleaning.convert_types(df, column_types)
        #df = DataCleaning.handle_missing(df)
        df = DataCleaning.remove_duplicates(df)
        #df = DataCleaning.remove_outliers(df, column)
        return df