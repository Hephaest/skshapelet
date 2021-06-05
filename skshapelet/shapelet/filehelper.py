import csv, os
from skshapelet.shapelet.shapelet_set import ShapeletSet

MODULE = os.path.dirname(__file__)
ARCHIVE_NAME = "shapelet"

def write_shapelets_to_csv(dataset_name, model_id, distinct_class, shapelets):
    """A simple function to save the shapelets obtained in csv format.

    Args:
        dataset_name: string
            The name of the dataset.
        model_id: string
            Unique id of the current model.
        shapelets: array-like
            The shapelets obtained for a dataset.
        distinct_class: array-like
            The distinct class of shapelets.
    """
    # Create directory in case it doesn't exists
    save_path = os.path.join(MODULE, ARCHIVE_NAME + '/' + dataset_name + '_' + model_id)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

        stack_by_class = {i: ShapeletSet() for i in distinct_class}

        file_path = save_path + '/class_all.csv'

        # write all shapelets in one file
        with open(file_path, "w+", newline="") as f:
            csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([
                "start_pos",
                "end_pos",
                "id",
                "label",
                "info_gain",
                "length",
                "ref_id",
            ])
            # Writing information
            for shapelet in shapelets:
                stack_by_class[shapelet.label].accept(shapelet)
                csv_writer.writerow([
                    shapelet.start_pos,
                    shapelet.end_pos,
                    shapelet.id,
                    shapelet.label,
                    shapelet.info_gain,
                    shapelet.length,
                    len(stack_by_class[shapelet.label].get_shapelets()) - 1,
                ])

        labels = []
        # Write distinct shapelets in different files
        for idx in distinct_class:
            file_path = save_path + '/' + 'class_' + str(idx) +'.csv'

            count = len(stack_by_class[idx].get_shapelets())
            if count == 0:
                continue

            labels.append(idx)
            with open(file_path, "w+", newline="") as f:
                csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow([
                    "start_pos",
                    "end_pos",
                    "id",
                    "label",
                    "info_gain",
                    "length"
                ])
                # Writing information
                for shapelet in stack_by_class[idx].get_shapelets():
                    csv_writer.writerow([
                        shapelet.start_pos,
                        shapelet.end_pos,
                        shapelet.id,
                        shapelet.label,
                        shapelet.info_gain,
                        shapelet.length
                    ])

        # Save labels for further reuse
        label_path = save_path + '/labels.csv'
        with open(label_path, "w+", newline="") as f:
            csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(labels)


def get_all_labels_from_csv(dataset_name, model_id):
    """A simple function to get all labels in csv format according to the current model id.

    Args:
        dataset_name: string
            The name of the dataset.
        model_id: string
            Unique id of the current model.

    Returns:
        output: list
            A list of distinct labels.
    """
    file_path = os.path.join(MODULE, ARCHIVE_NAME + '/' + dataset_name + '_' + model_id + '/labels.csv')
    with open(file_path, "r") as f:
        csv_reader = csv.reader(f, delimiter=',')
        return list(csv_reader)[0]


def get_all_index_by_label_from_csv(dataset_name, model_id, label):
    """A simple function to get all indexes according to the current model id and label.

    Args:
        dataset_name: string
            The name of the dataset.
        model_id: string
            Unique id of the current model.
        label: string
            The name of the label.

    Returns:
        output: list
            A list of all indexes.
    """
    folder_path = os.path.join(MODULE, ARCHIVE_NAME + '/' + dataset_name + '_' + model_id)
    file_path = folder_path + '/' + 'class_' + label + '.csv'
    with open(file_path, "r") as f:
        csv_reader = csv.reader(f, delimiter=',')
        length = len(list(csv_reader))
        return [i for i in range(1, length)]


def get_all_shapelets_from_csv(dataset_name, model_id):
    """A simple function to get all shapelets in csv format according to the current model id.

    Args:
        dataset_name: string
            The name of the dataset
        model_id: string
            Unique id of the current model

    Returns:
        output: list
            A list of all shapelets
    """
    file_path = os.path.join(MODULE, ARCHIVE_NAME + '/' + dataset_name + '_' + model_id + '/class_all.csv')
    rows = []
    with open(file_path, "r") as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            rows.append(row)
        return rows


def get_shapelet_by_label_index_from_csv(dataset_name, model_id, label, index):
    """A simple function to get the shapelet by the current model id, label and index.

    Args:
        dataset_name: string
            The name of the dataset
        model_id: string
            Unique id of the current model
        label: string
            The name of the label.
        index: int
            The order number of the index.

    Returns:
        output: list
            A list of shapelet information.
    """
    folder_path = os.path.join(MODULE, ARCHIVE_NAME + '/' + dataset_name + '_' + model_id)
    file_path = folder_path + '/' + 'class_' + label + '.csv'
    with open(file_path, "r") as f:
        csv_reader = csv.reader(f, delimiter=',')
        rows = list(csv_reader)

    return rows[index]