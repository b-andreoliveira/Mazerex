def append_weight(weight=[]):
    weight_list.update({"Weight": [weight_data]})
    weight_list.update({"Date_Time": [datetime.now]})

    df_w = pd.DataFrame(weight_list)
    print(df_w)

    if not os.path.isfile(animaltag + "_weight.csv"):
        df_w.to_csv(animaltag + "_weight.csv", encoding = "utf-8-sig", index = False)
    else:
        df_w.to_csv(animaltag + "_weight.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)


def append_rotation(cycles_str=[], event_type=[]):
    wheel_rotation.update({"Rotation": [cycles_str]})
    wheel_rotation.update({"Type": [event_type]})
    wheel_rotation.update({"Date_Time": [datetime.now]})

    df_r = pd.DataFrame(wheel_list)
    print(df_r)

    if not os.path.isfile(animaltag + "_rotations.csv"):
        df_r.to_csv(animaltag + "_rotations.csv", encoding = "utf-8-sig", index = False)
    else:
        df_r.to_csv(animaltag + "_rotations.csv", mode = "a+", header = False, encoding = "utf-8-sig", index = False)


weight_list = {
    "Weight" : [],
    "Date_Time": []
}

rotation_list = {
    "Rotation": [],
    "Type": [],
    "Date_Time": []
}