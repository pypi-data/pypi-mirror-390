import os
import pygsheets
import pandas as pd
import re
import datetime as dt
import requests as r


class instance():
    def __init__(self, **kwargs):
        if "env_object" in kwargs:
            self.client = pygsheets.authorize(service_account_env_var=kwargs["env_object"])
        self.spreadsheets = self.client.spreadsheet_titles()
        if "spreadsheet_name" in kwargs:
            self.spreadsheet = self.client.open(kwargs["spreadsheet_name"])


class SpreadsheetExtract(object):
    def __init__(self, spreadsheet_name, gs):
        self.ss = gs.client.open(spreadsheet_name)
        self.worksheets = [i for i in self.ss.worksheets() if re.fullmatch("[0-9]{3,4}", i.title)]
        self.tables_location = [
            ("work_distribution", "A64", "J68"),
            ("time_plan", "A72", "K86"),
            ("color_size_distribution", "B54", "I61"),
            ("kpis", "L65", "AL66"),
            ("material", "A2", "J8"),
            ("material_galantery", "A10", "K15"),
            ("work_details", "L67", "AH77"),
            ("products_distribution_PCE", "B140", "J147"),
            ("products_distribution_B", "B149", "J156"),
            ("products_distribution_ZL", "B158", "J165"),
            ("products_distribution_HK", "B167", "J174"),
            ("products_distribution_KH", "B176", "J183"),
            ("products_distribution_E", "B194", "J201")
        ]
        self.destinations = ["PCE", "B", "ZL", "HK", "KH", "E"]
        if len(self.worksheets) > 0:
            self.actual_worksheet = self.worksheets[0]
            self.title = self.actual_worksheet.title

    def find_table_coordinates(self, table_type):
        coordinates = [i for i in self.tables_location if table_type in i[0]][0]
        return coordinates[1], coordinates[2]

    def get_table_by_coordinates(self, table_type):
        start, end = self.find_table_coordinates(table_type)
        table = self.actual_worksheet.get_as_df(start=start, end=end,
                                                empty_value=None,
                                                numericise_ignore=["all"],
                                                head=1,
                                                default_blank="",
                                                default_na=0,
                                                include_tailing_empty=True,
                                                )
        return table

    def get_products_distribution(self, destinations):
        for idx, destination in enumerate(destinations):
            data = self.get_table_by_coordinates(f"products_distribution_{destination}")
            data.columns = ["color", "3-6kg", "6-9kg", "9-12kg", "1-3roky", "3+", "9+", "7-9let", "9-11let"]
            data = data.loc[:, (data != 0).any(axis=0)]
            data.dropna(inplace=True)
            try:
                data["color"] = data["color"].astype(int).astype(str)
            except:
                data["color"] = data["color"].astype(str)
            data["destination"] = destination
            data["task_id"] = self.title
            data = data.melt(["task_id", "color", "destination"], var_name="size", value_name="pieces")
            data.set_index(["task_id", "destination", "size", "color"], inplace=True)
            if idx == 0:
                products_distribution = data
            else:
                products_distribution = pd.concat([products_distribution, data])
        return products_distribution

    def get_work_distribution(self):
        table = self.get_table_by_coordinates("work_distribution")
        table.columns = ["operation", "credits_unit", "credits_total"] + list(table.columns[3:])
        table["task_id"] = self.title
        table["credits_unit"] = table["credits_unit"].str.replace(",", '.').astype(float).fillna(0)
        table["credits_total"] = table["credits_total"].str.replace(",", '.').astype(float).fillna(0) if table[
                                                                                                             "credits_total"].dtype == "object" else \
            table["credits_total"].fillna(0)
        table.dropna(how="all", axis=1, inplace=True)
        general_view = table[["operation", "credits_unit", "credits_total", "task_id"]].set_index(
            ["task_id", "operation"])
        worker_distribution = table.drop(["credits_total"], axis=1).melt(
            id_vars=["operation", "credits_unit", "task_id"],
            var_name="worker",
            value_name="pieces").dropna(how="any", axis=0).set_index(["task_id", "worker", "operation"])
        return {"general_view": general_view, "work_distribution": worker_distribution}

    def get_kpis(self):
        t = self.get_table_by_coordinates("kpis")
        t.columns = ["ÚL", "product_id", "season", "pieces", "work_amount", "material_amount", "amount_total",
                     "retail_price_calculated", "retail_price_recommended", "retail_price_difference",
                     "credit_price_total",
                     "credit_price_pevny", "credit_price_obnitka", "credit_price_step", "credit_price_flatlock",
                     "credit_price_striharna", "credit_price_kontrola", "???", "term_ušití/postup", "term_foto",
                     "term_úkolák", "term_nastříhání", "term_rozdělení_práce", "term_ušití", "term_cena_rozdělovník",
                     "term_kontrola", "term_expedice"]
        t["ÚL"] = t["ÚL"].astype("str")
        t["source_URL"] = self.actual_worksheet.url
        t.set_index(["ÚL", "product_id"], inplace=True)
        t.drop("???", axis=1, inplace=True)
        for i in [i for i in t.columns if "amount" in i or "retail_price" in i]:
            t[i] = t[i].apply(lambda x: "".join(re.findall("-?[0-9]+", x)))
        for i in [i for i in t.columns if "credit_price" in i]:
            t[i] = t[i].apply(lambda x: x.replace(",", '.') if type(x) == str else x)
        for i in [i for i in t.columns if "term_" in i]:
            t[i] = t[i].apply(
                lambda x: dt.date(int(x.split("/")[2]), int(x.split("/")[0]), int(x.split("/")[1])).strftime(
                    "%Y-%m-%d") if "/" in str(x) else x)

        return t

    def get_time_plan(self):
        try:
            table = self.get_table_by_coordinates("time_plan")

            working_weeks = [
                dt.date(int(i.split("/")[2]), int(i.split("/")[1]), int(i.split("/")[0])).strftime("%Y-%m-%d")
                for
                i in
                [table.columns[0]] + list(table.columns[1::2])]
            realized = pd.Series(
                [dt.date(int(i.split('/')[2]), int(i.split('/')[1]), int(i.split('/')[0])).strftime(
                    "%Y-%m-%d") if "/" in i else i
                 for i in list(table.T[1:].T.fillna('').apply(lambda x: ''.join(x).strip(",."), axis=1))])
            plan_list = sorted(
                [working_weeks[0]] * 2 + [working_weeks[1]] * 4 + working_weeks[2:-1] * 2 + [working_weeks[-1]])
            plan = pd.Series(plan_list)
            plan_end = pd.Series(
                [(dt.datetime.strptime(i, "%Y-%m-%d") + dt.timedelta(days=4)).strftime('%Y-%m-%d') for i in plan_list])
            phases = pd.concat([table.iloc[:, 0], realized, plan, plan_end], axis=1)
            phases["task_id"] = self.title
            phases.columns = ["operation", "realized", "plan_start", "plan_end", "task_id"]
            phases = phases.set_index(["task_id", "operation"])
        except Exception as e:
            phases = pd.DataFrame()
            print(f"error! {str(e)}")
        return phases

    def get_color_size_distribution(self):
        table = self.get_table_by_coordinates("color_size_distribution")
        table = table.melt(id_vars=["barva"], var_name="velikost", value_name="kusy")
        table.dropna(how="any", axis=0, inplace=True)
        table.columns = ["color", "size", "pieces"]
        table["task_id"] = self.title
        table.set_index(["task_id", "color", "size"], inplace=True)
        return table

    def get_material(self):
        table = self.get_table_by_coordinates("material")
        t = table.dropna(subset=[None, "ks"], how="all", axis=0)
        t = t.loc[t["ks"] > 0].melt(id_vars=[None, "ks"], var_name="size", value_name="pieces").dropna(subset="pieces")
        t.columns = ["material", "unit_pieces", "specification", "pieces"]
        t["task_id"] = self.title
        t["pieces"] = [i if type(i) != str else float(i.replace(",", ".").replace("cm", "")) for i in t["pieces"]]
        t.set_index(["task_id", "specification", "material"], inplace=True)
        return t

    def get_material_galantery(self):
        table = self.get_table_by_coordinates("material_galantery")
        category = ["material"] + ["visačka"] * 2 + ["složení"] + ["reflex"] * 4 + ["guma"] * 3
        table.columns = [s + "_" for s in category] + table.columns
        t2 = table.set_index("material_galanterie").T.iloc[:, 0:2]
        t2["task_id"], t2["specification"] = self.title, "galanterie"
        t3 = table.set_index("material_galanterie").T.iloc[:, 3:5]
        t3["task_id"], t3["specification"] = self.title, "černá galanterie"
        t4 = pd.concat([t2, t3])
        t4.reset_index(inplace=True)
        t4.columns = ["material", "unit_pieces", "pieces", "task_id", "specification"]
        t4.set_index(["task_id", "specification", "material"], inplace=True)
        t4.fillna(0)
        return t4

    def extract_table(self, name):
        if name == "work_distribution":
            return self.get_work_distribution()
        elif name == "time_plan":
            return self.get_time_plan()
        elif name == "color_size_distribution":
            return self.get_color_size_distribution()
        elif name == "material":
            return self.get_material()
        elif name == "material_galantery":
            return self.get_material_galantery()
        elif name == "kpis":
            return self.get_kpis()
        elif name == "products_distribution":
            return self.get_products_distribution(self.destinations)
