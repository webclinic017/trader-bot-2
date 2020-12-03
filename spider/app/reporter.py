import logging
from typing import List

import quantstats


class Reporter(object):
    logger = logging.getLogger(__name__)

    def report(self, results, strategy, log=False) -> List:

        report_list = []

        if type(results) == strategy:
            report_list.append(self._report_single(results, log=log))

        elif type(results) is list \
                and type(results[0]) == list \
                and type(results[0][0]) == strategy:

            report_list = report_list + self.report_multiple(results, log=log)

        elif type(results) is list:
            report_list = report_list + self.report_multiple(results, log=log)

        else:
            self.logger.error("wtf")

        return report_list

    def _report_single(self, result, html=False, log=False):
        quantstats.extend_pandas()
        portfolio_stats = result.analyzers.getbyname('PyFolio')
        basic_stats = result.analyzers.getbyname('Basic_Stats')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)

        if html:
            quantstats.reports.html(returns, output='logs/stats.html', title='CloseSMA')

        cagr = quantstats.stats.cagr(returns)
        sharpe = quantstats.stats.sharpe(returns)
        sortino = quantstats.stats.sortino(returns)
        volatility = quantstats.stats.volatility(returns)
        win = quantstats.stats.avg_win(returns)
        loss = quantstats.stats.avg_loss(returns)
        drawdown = quantstats.stats.max_drawdown(returns)

        if log:
            self.logger.info('CAGR: {:.3f}'.format(cagr))
            self.logger.info('Sharpe: {:.3f}'.format(sharpe))
            self.logger.info('Sortino: {:.3f}'.format(sortino))
            self.logger.info('Volatility: {:.3f}'.format(volatility))
            self.logger.info('Avg Win: {:.5f}'.format(win))
            self.logger.info('Avg Loss: {:.5f}'.format(loss))
            self.logger.info('Max Drawdown: {:.5f}'.format(drawdown))
            self.print_trade_analysis(basic_stats.get_analysis())

        results = {
            'cagr': cagr,
            'sharpe': sharpe,
            'sortino': sortino,
            'volatility': volatility,
            'avg_win': win,
            'avg_loss': loss,
            'max_drawdown': drawdown,
        }

        return results

    def report_multiple(self, results, log=False):
        a = []
        for r in results:
            for s in r:
                a.append(self._report_single(s, log=log))

        return a

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
