import logging

import quantstats


class Reporter(object):
    logger = logging.getLogger(__name__)

    def report(self, results, strategy):
        if type(results) == strategy:
            self.report_single(results)

        elif type(results) is list and type(results) == strategy:
            for r in results:
                self.report_single(r)

        elif type(results) is list:
            self.report_multiple(results)

        else:
            self.logger.error("wtf")

    def report_single(self, result, html=False):
        quantstats.extend_pandas()
        portfolio_stats = result.analyzers.getbyname('PyFolio')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)

        if html:
            quantstats.reports.html(returns, output='logs/stats.html', title='CloseSMA')

        self.logger.info('CAGR: {:.3f}'.format(quantstats.stats.cagr(returns)))
        self.logger.info('Sharpe: {:.3f}'.format(quantstats.stats.sharpe(returns)))
        self.logger.info('Sortino: {:.3f}'.format(quantstats.stats.sortino(returns)))
        self.logger.info('Volatility: {:.3f}'.format(quantstats.stats.volatility(returns)))
        self.logger.info('Avg Win: {:.5f}'.format(quantstats.stats.avg_win(returns)))
        self.logger.info('Avg Loss: {:.5f}'.format(quantstats.stats.avg_loss(returns)))
        self.logger.info('Max Drawdown: {:.5f}'.format(quantstats.stats.max_drawdown(returns)))

        basic_stats = result.analyzers.getbyname('Basic_Stats')
        self.print_trade_analysis(basic_stats.get_analysis())

    def report_multiple(self, results):
        for r in results:
            for s in r:
                self.report_single(s)

    def print_trade_analysis(self, analyzer):
        total_open = analyzer.total.open
        total_closed = analyzer.total.closed
        total_won = analyzer.won.total
        total_lost = analyzer.lost.total
        win_streak = analyzer.streak.won.longest
        lose_streak = analyzer.streak.lost.longest
        pnl_net = round(analyzer.pnl.net.total, 2)
        strike_rate = (total_won / total_closed) * 100

        h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
        h2 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
        r1 = [total_open, total_closed, total_won, total_lost]
        r2 = [strike_rate, win_streak, lose_streak, pnl_net]

        if len(h1) > len(h2):
            header_length = len(h1)
        else:
            header_length = len(h2)

        print_list = [h1, r1, h2, r2]
        row_format = "{:<15}" * (header_length + 1)
        self.logger.info("Trade Analysis Results:")

        for row in print_list:
            self.logger.info(row_format.format('', *row))
