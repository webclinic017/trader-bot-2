class WalkforwardStability:

    def __init__(self, train_results: dict, test_results: dict,  train_size=4, test_size=1):
        self.train_results = train_results
        self.test_results = test_results
        self.train_size = train_size
        self.test_size = test_size


    def get_results(self):
        train_avg_return = self.train_results.get("avg_return")
        test_avg_return = self.test_results.get("avg_return")
        train_profit_ratio = self.train_results.get("profit_ratio")
        test_profit_ratio = self.test_results.get("profit_ratio")
        train_profit_factor = self.train_results.get("profit_factor")
        test_profit_factor = self.test_results.get("profit_factor")
        train_cagr = self.train_results.get("cagr")
        test_cagr = self.test_results.get("cagr")

        avg_return_stability = test_avg_return / train_avg_return
        profit_ratio_stability = test_profit_ratio / train_profit_ratio
        profit_factor_stability = test_profit_factor / train_profit_factor
        cagr_stability = test_cagr / train_cagr


        results = {
            "avg_return_stability": avg_return_stability,
            "profit_ratio_stability": profit_ratio_stability,
            "profit_factor_stability": profit_factor_stability,
            "cagr_stability": cagr_stability,
        }
        return results

